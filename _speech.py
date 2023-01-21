import audioop
import contextlib
import math
from collections import deque
from statistics import stdev, mean
import pyaudio
from vosk import Model, KaldiRecognizer
import speech_recognition as sr
import wave
import json
import os
import settings
import pyttsx3


class Menu:
    def get_ready(self):
        pass

    def play_failure_phrase(self):
        pass


menu = {
    "intents": {
        "init": {
            "examples": ["зеркало", "стекло", "стекляшка",
                         "ало", "mirror"],
            "responses": Menu().get_ready
        },
        "greeting": {
            "examples": ["привет", "здравствуй", "добрый день",
                         "hello", "good morning"],
            "responses": Menu.get_ready
        },
        "farewell": {
            "examples": ["пока", "до свидания", "увидимся", "до встречи",
                         "goodbye", "bye", "see you soon"],
            "responses": Menu.get_ready
        },
        "google_search": {
            "examples": ["найди в гугле", "search on google", "google", "find on google"],
            "responses": Menu.get_ready
        },
    },
    "failure_phrases": Menu.play_failure_phrase
}


class VoiceAssistant:
    def __init__(self):
        # настройка данных голосового помощника
        self.name = "Mirror"
        self.sex = "female"
        self.speech_language = "ru"

        self.assistant = None
        self.ttsEngine = pyttsx3.init()

        # self.assistant = VoiceAssistant()
        # self.assistant.name = "Mirror"
        # self.assistant.sex = "female"
        # self.assistant.speech_language = "ru"
        # voices = self.ttsEngine.getProperty("voices")
        # self.ttsEngine.setProperty("voice", voices[0].id)

    def play_voice_assistant_speech(self, text):
        self.ttsEngine.say(str(text))
        self.ttsEngine.runAndWait()


class SpeechData:
    AUDIO_FILENAME = "microphone_voice_block.wav"
    VAD_AGGRESSIVENESS = 2

    def __init__(self, app, audio_recorded_event):
        self.app = app
        self.audio_recorded = audio_recorded_event
        self.file = open(self.AUDIO_FILENAME, "wb")
        self.energy_threshold = settings.THRESHOLD
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(format=settings.FORMAT,
                                  channels=settings.CHANNELS,
                                  rate=settings.RATE,
                                  input=True,
                                  frames_per_buffer=settings.CHUNK)
        self.calibrate_silence_level(self.stream)

    def calibrate_silence_level(self, audio_stream, samples_count=10, iterations=5):
        print('calibrating')
        computed_threshold = deque(maxlen=samples_count)
        for _ in range(iterations):
            dynamic_threshold = deque(maxlen=samples_count)
            for _ in range(samples_count):
                buffer = audio_stream.read(settings.CHUNK)
                seconds_per_buffer = (settings.CHUNK + 0.0) / settings.RATE
                energy = audioop.max(buffer, 2)  # energy of the audio signal
                # dynamically adjust the energy threshold using asymmetric weighted average
                damping = 0.15 ** seconds_per_buffer  # account for different chunk sizes and rates
                target_energy = energy * 1.5
                dynamic_threshold.append(settings.THRESHOLD * damping + target_energy * (1 - damping))
            if stdev(dynamic_threshold) > 10:
                continue
            computed_threshold.append(mean(dynamic_threshold))

        if len(computed_threshold) > 3:
            print('calibrating done, silence level is:', mean(computed_threshold))
            self.energy_threshold = mean(computed_threshold) + 100

    def start(self, num_phrases=-1):
        stream = self.stream
        print("* Listening mic. ")
        audio2send = []
        rel = settings.RATE / settings.CHUNK
        slid_win = deque(maxlen=int(settings.SILENCE_LIMIT * rel))
        # Prepend audio from 0.5 seconds before noise was detected
        prev_audio = deque(maxlen=int(settings.PREV_AUDIO * rel))
        started = False
        n = num_phrases
        response = []

        while num_phrases == -1 or n > 0:
            threshold = self.energy_threshold
            cur_data = stream.read(settings.CHUNK)
            slid_win.append(math.sqrt(abs(audioop.avg(cur_data, 4))))
            if sum([x > threshold for x in slid_win]) > 0:
                if not started:
                    print("Starting record of phrase")
                    started = True
                audio2send.append(cur_data)
            elif started is True:
                print("Finished")
                print(type(list(prev_audio)), type(audio2send))

                self.save_speech(list(prev_audio) + audio2send, self.p)
                self.play_audio()
                exit()
                self.audio_recorded.set()
                print('audio_recorded event fired')
                # Reset all
                started = False
                slid_win = deque(maxlen=int(settings.SILENCE_LIMIT * rel))
                prev_audio = deque(maxlen=int(0.5 * rel))
                audio2send = []
                n -= 1
                print("Listening ...")
            else:
                prev_audio.append(cur_data)

        print("* Done recording")
        self.stream.close()
        self.p.terminate()

        return response

    def play_audio(self):
        with wave.open(self.AUDIO_FILENAME, 'rb') as wf:
            p = pyaudio.PyAudio()

            stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                            channels=wf.getnchannels(),
                            rate=wf.getframerate(),
                            output=True)

            while len(data := wf.readframes(settings.CHUNK)):
                print(audioop.max(data, 2))
                stream.write(data)

            stream.close()
            p.terminate()

    @staticmethod
    def save_speech(data, p):
        with contextlib.closing(wave.open(SpeechData.AUDIO_FILENAME, 'wb')) as wf:
            wf.setnchannels(1)
            wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
            wf.setframerate(16000)  # TODO make this value a function parameter?
            wf.writeframes(b''.join(data))
            wf.close()


class VoiceData:
    def __init__(self, app, audio_recorded_event):
        self.app = app
        self.audio_recorded = audio_recorded_event
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()

    def record_and_recognize_audio(self):
        recognized_data = ""
        try:
            self.app.logging.debug("Started recognition...")
            with sr.AudioFile(SpeechData.AUDIO_FILENAME) as source:
                audio = self.recognizer.record(source)
                recognized_data = self.recognizer.recognize_google(audio, language="ru").lower()

        except sr.UnknownValueError:
            pass

        except sr.RequestError:
            self.app.logging.debug("Trying to use offline recognition...")
            recognized_data = self.use_offline_recognition()

        os.remove(SpeechData.AUDIO_FILENAME)

        return recognized_data

    def use_offline_recognition(self):
        recognized_data = ""
        # проверка наличия модели на нужном языке в каталоге приложения
        if not os.path.exists("models/vosk-model-small-ru-0.4"):
            self.app.logging.debug("Please download the model from:\n"
                                   "https://alphacephei.com/vosk/models and unpack as 'model' in the current folder.")
            exit(1)
        try:
            # анализ записанного в микрофон аудио (чтобы избежать повторов фразы)
            wave_audio_file = wave.open("microphone-results.wav", "rb")
            model = Model("models/vosk-model-small-ru-0.4")
            offline_recognizer = KaldiRecognizer(model, wave_audio_file.getframerate())

            data = wave_audio_file.readframes(wave_audio_file.getnframes())
            if len(data) > 0:
                if offline_recognizer.AcceptWaveform(data):
                    recognized_data = offline_recognizer.Result()

                    # получение данных распознанного текста из JSON-строки
                    # (чтобы можно было выдать по ней ответ)
                    recognized_data = json.loads(recognized_data)
                    recognized_data = recognized_data["text"]
        except:
            self.app.logging.debug("Sorry, speech service is unavailable. Try again later")

        return recognized_data

    @staticmethod
    def execute_command_with_name(command_name: str, *args: list):
        command_name = str.lower(command_name)
        for key in menu.keys():
            if command_name in key:
                menu[key](*args)
            else:
                print("Command not found")

        # def prepare_corpus():
        #     """
        #     Подготовка модели для угадывания намерения пользователя
        #     """
        #     corpus = []
        #     target_vector = []
        #     for intent_name, intent_data in config["intents"].items():
        #         for example in intent_data["examples"]:
        #             corpus.append(example)
        #             target_vector.append(intent_name)
        #
        #     training_vector = vectorizer.fit_transform(corpus)
        #     classifier_probability.fit(training_vector, target_vector)
        #     classifier.fit(training_vector, target_vector)

    def start(self):
        while True:
            if self.audio_recorded.is_set():
                print('got it')
                self.audio_recorded.clear()
                voice_input = self.record_and_recognize_audio()
                if voice_input:
                    print(voice_input)
                    voice_input = voice_input.split(" ")
                    command = voice_input[0]
                    command_options = [str(input_part) for input_part in voice_input[1:len(voice_input)]]
                    self.execute_command_with_name(command, command_options)

from numpy import array
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import OneHotEncoder
from sklearn.svm import LinearSVC
from vosk import Model, KaldiRecognizer
import speech_recognition as sr
import wave
import json
import os
import settings
import pyttsx3

from toolbox import ToolBox

logging = ToolBox.get_logger('speech')


class Menu:
    def get_ready(self):
        pass

    def wake(self):
        pass

    def dismiss(self):
        pass

    def play_failure_phrase(self):
        pass

    def not_found(self):
        print('not found')


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


class VoiceData:
    def __init__(self, audio_recorded_event=None):
        self.intents = json.load(open(settings.INTENTS, 'r', encoding='utf-8'))
        self.audio_recorded = audio_recorded_event
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()

    def record_and_recognize_audio(self):
        recognized_data = ""
        try:
            logging.debug("Started recognition...")
            with sr.AudioFile(settings.AUDIO_STORAGE) as source:
                audio = self.recognizer.record(source)
                recognized_data = self.recognizer.recognize_google(audio, language="ru").lower()

        except sr.UnknownValueError:
            pass

        except sr.RequestError:
            logging.debug("Trying to use offline recognition...")
            recognized_data = self.use_offline_recognition()

        os.remove(settings.AUDIO_STORAGE)

        return recognized_data

    def use_offline_recognition(self):
        recognized_data = ""
        # проверка наличия модели на нужном языке в каталоге приложения
        if not os.path.exists("models/vosk-model-small-ru-0.4"):
            logging.debug("Please download the model from:\n"
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
                    recognized_data = json.loads(recognized_data)
                    recognized_data = recognized_data["text"]
        except:
            logging.debug("Sorry, speech service is unavailable. Try again later")

        return recognized_data

    def execute_command_with_name(self, command_name: str, *args: list):
        command_name = str.lower(command_name)
        for key in self.intents['intents'].keys():
            if command_name in key:
                getattr(Menu(), self.intents['intents'][key]['callable'])(*args)
        Menu().not_found()

    def prepare_corpus(self):
        # Подготовка модели
        corpus = []
        target_vector = []

        intents = json.load(open(self.intents, 'r', encoding='utf-8'))
        for intent_name, intent_data in intents['intents'].items():
            for example in intent_data["examples"]:
                corpus.append(example)
                target_vector.append(intent_name)

        vectorizer = TfidfVectorizer()
        training_vector = vectorizer.fit_transform(corpus)

        model = LinearSVC()
        model.fit(training_vector, target_vector)

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


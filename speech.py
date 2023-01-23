""" speech recognition module """
import json
import os
import sys
import wave

import pyttsx3
import speech_recognition as sr # pylint: disable=E0401
from sklearn.feature_extraction.text import TfidfVectorizer # pylint: disable=E0401
from sklearn.svm import LinearSVC # pylint: disable=E0401
from vosk import Model, KaldiRecognizer

import settings
from toolbox import ToolBox

logger = ToolBox.get_logger('speech')


class Menu:
    """
    functions list
    """

    def get_ready(self):
        """
        get ready to next command
        """

    def wake(self):
        """
        rise and shine
        """

    def dismiss(self):
        """
        bye
        """

    def play_failure_phrase(self):
        """
        not found
        """

    def not_found(self):
        """
        not found
        """
        print('not found')


class VoiceAssistant:
    """
    voice assistant class
    """

    def __init__(self):
        # настройка данных голосового помощника
        self.name = "Mirror"
        self.sex = "female"
        self.speech_language = "ru"

        self.assistant = None
        self.tts_engine = pyttsx3.init()

        # self.assistant = VoiceAssistant()
        # self.assistant.name = "Mirror"
        # self.assistant.sex = "female"
        # self.assistant.speech_language = "ru"
        # voices = self.ttsEngine.getProperty("voices")
        # self.ttsEngine.setProperty("voice", voices[0].id)

    def play_voice_assistant_speech(self, text):
        """
        play voice
        """
        self.tts_engine.say(str(text))
        self.tts_engine.runAndWait()


class VoiceData:
    """
    speech recognition
    """

    def __init__(self, audio_recorded_event=None):
        self.intents = settings.INTENTS
        self.audio_recorded = audio_recorded_event
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()

    def recognize_and_remove_audio(self):
        """
        recognize and remove
        """

        recognized_data = ""
        try:
            logger.debug("Started recognition...")
            with sr.AudioFile(settings.AUDIO_STORAGE) as source:
                audio = self.recognizer.record(source)
                recognized_data = self.recognizer.recognize_google(audio, language="ru").lower()

        except sr.UnknownValueError:
            pass

        except sr.RequestError:
            logger.debug("Trying to use offline recognition...")
            recognized_data = self.use_offline_recognition()

        os.remove(settings.AUDIO_STORAGE)

        return recognized_data

    @staticmethod
    def use_offline_recognition():
        """
        vosk recognizer
        """

        recognized_data = ""
        # проверка наличия модели на нужном языке в каталоге приложения
        if not os.path.exists("models/vosk-model-small-ru-0.4"):
            logger.debug("Please download the model from:\n"
                         "https://alphacephei.com/vosk/models and unpack as 'model'"
                         " in the current folder.")
            sys.exit(1)
        # try:

        # анализ записанного в микрофон аудио (чтобы избежать повторов фразы)
        wave_audio_file = wave.open(settings.AUDIO_STORAGE, "rb")
        model = Model("models/vosk-model-small-ru-0.4")
        offline_recognizer = KaldiRecognizer(model, wave_audio_file.getframerate())

        data = wave_audio_file.readframes(wave_audio_file.getnframes())
        if len(data) > 0:
            if offline_recognizer.AcceptWaveform(data):
                recognized_data = offline_recognizer.Result()
                recognized_data = json.loads(recognized_data)
                recognized_data = recognized_data["text"]
        # except:
        #     logger.debug("Sorry, speech service is unavailable. Try again later")

        return recognized_data

    def execute_command_by_name(self, command_name: str, *args: list):
        """
        execute
        """
        command_name = str.lower(command_name)
        with json.load(open(self.intents, 'r', encoding='utf-8')) as intents:
            for key in intents['intents'].keys():
                if command_name in key:
                    getattr(Menu(), intents['intents'][key]['callable'])(*args)
            Menu().not_found()

    def prepare_corpus(self):
        """
        model preparation
        """
        corpus = []
        target_vector = []

        with json.load(open(self.intents, 'r', encoding='utf-8')) as intents:
            for intent_name, intent_data in intents['intents'].items():
                for example in intent_data["examples"]:
                    corpus.append(example)
                    target_vector.append(intent_name)

        vectorizer = TfidfVectorizer()
        training_vector = vectorizer.fit_transform(corpus)

        model = LinearSVC()
        model.fit(training_vector, target_vector)

    def start(self):
        """
        main loop for voice recognition
        and command completion
        :return:
        """
        while True:
            if self.audio_recorded.is_set():
                print('got it')
                self.audio_recorded.clear()
                voice_input = self.recognize_and_remove_audio()
                if voice_input:
                    print(voice_input)
                    voice_input = voice_input.split(" ")
                    command = voice_input[0]
                    command_options = [str(input_part) for input_part in
                                       voice_input[1:len(voice_input)]]
                    self.execute_command_by_name(command, command_options)

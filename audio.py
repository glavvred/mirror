""" Module audiorecorder """
import audioop
import contextlib
import math
import os
import wave
from collections import deque
from threading import Event

import pyaudio  # pylint: disable=E0401

import settings


class AudioRecorder:
    """
    Listen to microphone,
    record cuts if any,
    write files
    """
    p = pyaudio.PyAudio()

    def __init__(self, audio_recorded_event: Event = None):
        self.audio_recorded = audio_recorded_event
        self.stream = self.p.open(format=settings.FORMAT,
                                  channels=settings.CHANNELS,
                                  rate=settings.RATE,
                                  input=True,
                                  frames_per_buffer=settings.CHUNK)

    def start(self, num_phrases=-1):
        """
        Capture given number of phrases or till silence comes
        :param num_phrases:
        :return: None
        """
        stream = self.stream
        print("* Listening mic. ")
        audio2send = []
        rel = settings.RATE / settings.CHUNK
        slid_win = deque(maxlen=int(settings.SILENCE_LIMIT * rel))
        # Prepend audio from 0.5 seconds before noise was detected
        prev_audio = deque(maxlen=int(settings.PREV_AUDIO * rel))
        started = False
        current_num = 0
        while num_phrases == -1 or current_num > 0:
            threshold = settings.THRESHOLD
            cur_data = stream.read(settings.CHUNK)
            slid_win.append(math.sqrt(abs(audioop.avg(cur_data, 4))))
            if sum(x > threshold for x in slid_win) > 0:  # silence is broken
                if not started:
                    started = True
                audio2send.append(cur_data)
            elif started is True:
                self.save_file(list(prev_audio) + audio2send)
                # self.play_audio() # testing
                self.audio_recorded.set()  # flag for audio recognition daemon
                # Reset all
                started = False
                slid_win = deque(maxlen=int(settings.SILENCE_LIMIT * rel))
                prev_audio = deque(maxlen=int(0.5 * rel))
                audio2send = []
                current_num -= 1
                print("Listening ...")
            else:
                prev_audio.append(cur_data)

    def play_audio(self):
        """
        Playback for testing
        :return:
        """
        with wave.open(settings.AUDIO_FILENAME, 'rb') as wave_file:
            stream = self.p.open(format=self.p.get_format_from_width(wave_file.getsampwidth()),
                                 channels=wave_file.getnchannels(),
                                 rate=wave_file.getframerate(),
                                 output=True)

            while len(data := wave_file.readframes(settings.CHUNK)):
                stream.write(data)

            stream.close()
            self.p.terminate()

    def save_file(self, data):
        """
        Write down captured audio part
        :param data:
        :return:
        """
        with contextlib.closing(wave.open(settings.AUDIO_FILENAME, 'wb')) as wave_file:
            wave_file.setnchannels(1)
            wave_file.setsampwidth(self.p.get_sample_size(pyaudio.paInt16))
            wave_file.setframerate(16000)
            wave_file.writeframes(b''.join(data))
            wave_file.close()

    def __del__(self):
        """
        clear your tracks
        :return:
        """
        print("* Done recording")
        os.remove(settings.AUDIO_FILENAME)
        self.stream.close()
        self.p.terminate()

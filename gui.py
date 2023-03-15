import faulthandler
import logging
import threading
import sys
import time

import numpy as np
import tkinter as tk
from tkinter import *
from tkinter import ttk

from PIL import ImageTk, Image

import settings
from mirror import Mirror
from news import NewsMethods
from settings import NEWS_COUNT
from weather import WeatherMethods
from audio import AudioRecorder
from camera import CameraData
from faces import FaceData
from motion import MotionData
from speech import VoiceData
from toolbox import ToolBox

from dbase.connection import DbConnect
from dbase.models import Condition, User


class Clock:
    days = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"]
    months = ["Января", "Февраля", "Марта", "Апреля", "Мая", "Июня", "Июля", "Августа", "Сентября",
              "Октября", "Ноября", "Декабря"]

    def __init__(self, root):
        clock_date_node = tk.Frame(root)
        clock_date_node.configure(background='black')
        clock_date_node.pack(side=LEFT, padx=15)
        date_node = tk.Frame(clock_date_node, bg='black')
        date_node.pack()

        self.clock_date = tk.Label(date_node, font=('Tahoma', 20), bg='black', fg='white')
        self.clock_date.pack(in_=date_node, side=TOP)

        clock_node = tk.Frame(clock_date_node, bg='black', padx=20)
        clock_node.pack()

        self.clock_hours = tk.Label(clock_node, font=('Tahoma', 30), bg='black', fg='white')
        self.clock_min_sec = tk.Label(clock_node, font=('Tahoma', 30), bg='black', fg='white')

        self.clock_hours.pack(in_=clock_node, side=LEFT)
        self.clock_min_sec.pack(in_=clock_node, side=LEFT)

    def hour_timer(self, time1=''):
        time2 = time.strftime("%H")
        if time2 != time1:
            time1 = time2
            self.clock_hours.config(text=time2)
        self.clock_hours.after(200, self.hour_timer)

    def minutes_seconds_timer(self, time1=''):
        time2 = time.strftime(":%M:%S")
        if time2 != time1:
            time1 = time2
            self.clock_min_sec.config(text=time2)
        self.clock_min_sec.after(200, self.minutes_seconds_timer)

    def date(self):
        day = self.days[time.localtime()[6]]
        month = self.months[time.localtime()[1] - 1]
        clock_date = day + " " + time.strftime("%d") + " " + month
        self.clock_date.config(text=clock_date)
        self.clock_date.after(500, self.date)


class SplashScreen:
    def __init__(self):
        startupscreen = self.startupscreen = tk.Tk()
        self.progress = DoubleVar(value=0)
        startupscreen.title('Mirror Mirror')
        startupscreen.configure(background='black')
        startupscreen.overrideredirect(True)
        welcometext = tk.Label(startupscreen, font=('arial', 40), bg='black', fg='white')
        welcometext.config(text='Hello dearest')
        welcometext.pack(side=TOP, padx=120, pady=20)
        self.progressbar = ttk.Progressbar(startupscreen, orient='horizontal', mode='determinate',
                                           length=280, variable=self.progress)
        self.progressbar.pack(side=TOP, padx=20, pady=10)
        # Gets the requested values of the height and width.
        window_width = startupscreen.winfo_reqwidth()
        window_height = startupscreen.winfo_reqheight()
        # Gets both half the screen width/height and window width/height
        position_right = int(startupscreen.winfo_screenwidth() / 3 - window_width / 2)
        position_down = int(startupscreen.winfo_screenheight() / 2 - window_height / 2)

        # Positions the window in the center of the page.
        startupscreen.geometry("+{}+{}".format(position_right, position_down))
        startupscreen.update()

    def end(self):
        self.startupscreen.destroy()

    def increase(self, increment: float):
        self.progress.set(self.progress.get() + increment)
        self.startupscreen.update()


class NewsNode:
    def __init__(self, root):
        import textwrap

        news_node = tk.Frame(root, background='black')
        news_node.pack(anchor=E)
        news_widget = tk.Frame(news_node, height=NEWS_COUNT, bg='black', pady=20)
        for article in NewsMethods.get_last(NEWS_COUNT):
            news_image = Image.open('static/assets/Newspaper.png')
            news_image = ImageTk.PhotoImage(news_image.resize((20, 20), Image.LANCZOS))
            article_text = textwrap.fill(article.title, break_long_words=False,
                                         break_on_hyphens=False)
            article_node = tk.Label(news_widget, font=('Tahoma', 10), bg='black', fg='white',
                                    width=500, text=article_text, compound=LEFT, image=news_image,
                                    justify=RIGHT, anchor=E, padx=5)
            article_node.image = news_image
            article_node.pack(in_=news_widget, anchor=E, side=TOP, padx=0, pady=0)

        news_widget.pack()


def leave(event):
    root_node.destroy()
    # destroy daemons
    sys.exit()


class WeatherNode:
    directions = {"n": "↑", "ne": "↗", "e": "→", "se": "↘", "s": "↓", "sw": "↙", "w": "←",
                  "nw": "↖"}
    day_parts = {"morning": "утро", "day": "день", "evening": "вечер", "night": "ночь"}

    def __init__(self, root):
        weather = WeatherMethods.get_last()

        weather_node = tk.Frame(root, height=30, width=100, bg='black')
        weather_node.pack(side=RIGHT)

        top_frame = tk.Frame(weather_node, height=30, width=150, bg='black')
        top_frame.pack(in_=weather_node, side=TOP, fill="x")

        # sunrise - sunset
        if int(time.strftime("%H")) > 12:
            sunrise_text = f'{weather.sunset:%H:%M}'
        else:
            sunrise_text = f'{weather.sunrise:%H:%M}'
        sunrise_image = Image.open('static/assets/Sunrise.png')
        sunrise_image = ImageTk.PhotoImage(sunrise_image.resize((20, 20), Image.LANCZOS))
        sunrise_node = tk.Label(top_frame, font=('Tahoma', 20), bg='black', fg='white',
                                padx=5, text=sunrise_text, compound=LEFT, image=sunrise_image)
        sunrise_node.image = sunrise_image
        sunrise_node.pack(in_=top_frame, side=LEFT, fill='x', expand=True)

        # wind gust
        wind_gust_text = f'({weather.wind_gust})'
        wind_gust_node = tk.Label(top_frame, font=('Tahoma', 15), bg='black', fg='white',
                                  text=wind_gust_text, compound=LEFT)
        wind_gust_node.pack(in_=top_frame, side=RIGHT)

        # wind dir and speed
        wind_text = f'{self.directions[weather.wind_dir]} {weather.wind_speed}м/с'
        wind_image = Image.open('static/assets/Wind.png')
        wind_image = ImageTk.PhotoImage(wind_image.resize((20, 20), Image.LANCZOS))
        wind_node = tk.Label(top_frame, font=('Tahoma', 20), bg='black', fg='white',
                             text=wind_text, compound=LEFT, image=wind_image)
        wind_node.image = wind_image
        wind_node.pack(in_=top_frame, side=RIGHT, fill='x', expand=True)

        # mid frame
        middle_frame = tk.Frame(weather_node, height=30, width=100, bg='black')
        middle_frame.pack(in_=weather_node, side=TOP, fill='x')

        # temp - feels_like now
        text_feels_like = f'({weather.feels_like})'
        temp_feels_like = tk.Label(middle_frame, font=('Tahoma', 20), bg='black', fg='white',
                                   padx=5, compound=RIGHT, text=text_feels_like)
        temp_feels_like.pack(in_=middle_frame, side=RIGHT)

        # condition now
        condition_image = Image.open(f'static/assets/{weather.condition.icon}.png')
        condition_image = ImageTk.PhotoImage(condition_image.resize((50, 50), Image.LANCZOS))
        temp_text = str(weather.temperature) + '°'
        temp_node = tk.Label(middle_frame, font=('Tahoma', 40), bg='black', fg='white',
                             padx=5, text=temp_text, compound=LEFT, image=condition_image)
        temp_node.image = condition_image
        temp_node.pack(in_=middle_frame, side=RIGHT)

        lower_frame = tk.Frame(weather_node, bg='green')
        lower_frame.pack(in_=weather_node, side=BOTTOM, anchor=E)

        for forecast_part in weather.forecast_parts:
            p_condition_image = Image.open(f'static/assets/{forecast_part.condition.icon}.png')
            p_condition_image = ImageTk.PhotoImage(
                p_condition_image.resize((15, 15), Image.LANCZOS))
            p_temp_text = f' {self.day_parts[forecast_part.part_name]} {forecast_part.temp_min}°/' \
                          f'{forecast_part.temp_max}° ({forecast_part.feels_like})'
            p_temp_node = tk.Label(lower_frame, font=('Tahoma', 15), bg='black', fg='white',
                                   text=p_temp_text, anchor=E, compound=LEFT,
                                   image=p_condition_image)
            p_temp_node.image = p_condition_image
            p_temp_node.pack(in_=lower_frame, anchor=E, side=TOP, fill='x', expand=True)


class FaceNode:
    def __init__(self, root):
        from collections import deque
        face_node = tk.Frame(root, height=30, width=100, bg='red')
        face_node.pack(side=LEFT)
        self.webcam_image_node = tk.Label(root, font=('Tahoma', 15), bg='black', fg='white')
        self.webcam_image_node.pack(in_=face_node, side=LEFT)
        self.movement_detected_node = tk.Label(root, font=('Tahoma', 15), bg='black', fg='white')
        self.movement_detected_node.pack(in_=face_node, side=LEFT)
        self.face_detected_node = tk.Label(root, font=('Tahoma', 15), bg='black', fg='white')
        self.face_detected_node.pack(in_=face_node, side=LEFT)
        self.frame_times = deque([0] * 5)
        self.current_frame = settings.LAST_FRAME

    def show_webcam(self):
        if np.array_equal(self.current_frame, settings.LAST_FRAME):
            pass
        self.current_frame = settings.LAST_FRAME

        self.frame_times.rotate()
        self.frame_times[0] = time.time()
        sum_of_deltas = self.frame_times[0] - self.frame_times[-1]
        count_of_deltas = len(self.frame_times) - 1
        try:
            fps = int(float(count_of_deltas) / sum_of_deltas)
        except ZeroDivisionError:
            fps = 0

        rgb_weights = [0.2989, 0.5870, 0.1140]
        grayscale_image = np.dot(settings.LAST_FRAME, rgb_weights)
        face_image = ImageTk.PhotoImage(image=Image.fromarray(grayscale_image))
        self.webcam_image_node.config(image=face_image, text='FPS: {}'.format(fps), compound='bottom')
        self.webcam_image_node.image = face_image
        self.webcam_image_node._image_cache = face_image

        self.webcam_image_node.after(10, func=lambda: self.show_webcam())

    def movement_detected(self):
        if settings.MOTION_DETECTED:
            self.movement_detected_node.config(text='movement')
        else:
            self.movement_detected_node.config(text='still')
        self.movement_detected_node.after(10, func=lambda: self.movement_detected())

    def face_detected(self):
        if settings.MATCHED_USERS:
            greetings = ''
            for face_id in settings.MATCHED_USERS:
                user = session.query(User).filter(User.id == face_id).first()
                greetings = f'{greetings}, {user.name}, have a good day'
            self.face_detected_node.config(text=f'hello {greetings}')
        else:
            self.face_detected_node.config(text='no face')
        self.face_detected_node.after(10, func=lambda: self.face_detected())


if __name__ == '__main__':

    ss = SplashScreen()
    # load daemons
    faulthandler.enable()
    mirror = ToolBox().start_mirror()
    logger = ToolBox().get_logger("main", logging.DEBUG)

    session = DbConnect.get_session()
    if session.query(Condition).count() == 0:  # пустая таблица condition
        Condition.fill_base_data()
    ToolBox.create_folders_if_not_exist()
    time.sleep(0.2)
    ss.increase(20)

    thread = threading.Thread(name='news_daemon', target=NewsMethods().start)
    thread.setDaemon(True)
    thread.start()
    ss.increase(20)

    thread = threading.Thread(name='weather_daemon', target=WeatherMethods().start)
    thread.setDaemon(True)
    thread.start()
    time.sleep(0.2)
    ss.increase(20)

    c_d = threading.Thread(name='camera_daemon', target=CameraData().start)
    c_d.setDaemon(True)
    c_d.start()
    m_d = threading.Thread(name='motion_daemon', target=MotionData().detect_motion)
    m_d.setDaemon(True)
    m_d.start()
    fr_d = threading.Thread(name='face_recognition_daemon', target=FaceData().start)
    fr_d.setDaemon(True)
    fr_d.start()
    time.sleep(0.2)
    ss.increase(20)

    audio_recorded = threading.Event()
    ar_d = threading.Thread(name='audio_recording_daemon',
                            target=AudioRecorder(audio_recorded).start)
    ar_d.setDaemon(True)
    ar_d.start()
    vr_d = threading.Thread(name='voice_recognition_daemon', target=VoiceData(audio_recorded).start)
    vr_d.setDaemon(True)
    vr_d.start()
    time.sleep(0.2)
    ss.increase(20)
    ss.end()

    root_node = tk.Tk()
    root_node.bind('<Escape>', leave)
    root_node.attributes("-fullscreen", True)
    root_node.configure(background='black')

    top_row = tk.Frame(root_node, bg='black')
    mid_row = tk.Frame(root_node, bg='black')
    bot_row = tk.Frame(root_node, bg='black', height=70)
    top_row.pack(side=TOP, fill="x", expand=False)
    mid_row.pack(side=TOP, fill="both", expand=True)
    bot_row.pack(side=BOTTOM, fill="x", expand=False)

    WeatherNode(top_row)
    clock = Clock(top_row)

    NewsNode(mid_row)
    face = FaceNode(mid_row)
    face_t = threading.Thread(name='webcam_image', target=face.show_webcam())
    face_t.start()
    # face_t2 = threading.Thread(name='webcam_image2', target=face.movement_detected())
    # face_t2.start()
    face_t3 = threading.Thread(name='webcam_image3', target=face.face_detected())
    face_t3.start()

    while True:
        clock.hour_timer()
        clock.minutes_seconds_timer()
        clock.date()

        root_node.mainloop()

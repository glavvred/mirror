import sys
import time
import tkinter as tk
from tkinter import *
from tkinter import ttk

from PIL import ImageTk, Image

from news import NewsMethods
from settings import NEWS_COUNT
from weather import WeatherMethods


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
        windowWidth = startupscreen.winfo_reqwidth()
        windowHeight = startupscreen.winfo_reqheight()
        # Gets both half the screen width/height and window width/height
        positionRight = int(startupscreen.winfo_screenwidth() / 3 - windowWidth / 2)
        positionDown = int(startupscreen.winfo_screenheight() / 2 - windowHeight / 2)

        # Positions the window in the center of the page.
        startupscreen.geometry("+{}+{}".format(positionRight, positionDown))
        startupscreen.update()

    def end(self):
        print('here')
        self.startupscreen.destroy()

    def increase(self, increment: float):
        self.progress.set(self.progress.get() + increment)
        self.startupscreen.update()


class NewsNode:
    def __init__(self, root):
        news_node = tk.Frame(root)
        news_node.configure(background='black')
        news_node.pack(anchor=E, padx=5)
        news_widget = tk.Frame(news_node, height=NEWS_COUNT, width=100, bg='black')
        for article in NewsMethods.get_last(NEWS_COUNT):
            news_image = Image.open('static/assets/Newspaper.png')
            news_image = ImageTk.PhotoImage(news_image.resize((20, 20), Image.LANCZOS))
            article_node = tk.Label(news_widget, font=('Tahoma', 10), bg='black', fg='white',
                                    width=400, padx=5, text=article.title, compound=LEFT,
                                    image=news_image)
            article_node.image = news_image
            article_node.pack(in_=news_widget, side=TOP, expand=True, padx=0, pady=0)

        news_widget.pack()


def leave(event):
    root_node.destroy()
    sys.exit()


class WeatherNode:
    directions = {"n": "↑ N", "ne": "↗ NE", "e": "→ E", "se": "↘ SE", "s": "↓ S", "sw": "↙ SW",
                  "w": "← W", "nw": "↖ NW"}

    def __init__(self, root):
        weather = WeatherMethods.get_last()
        print(weather.temperature, weather.feels_like, weather.feels_like, weather.wind_speed,
              weather.wind_dir)
        weather_node = tk.Frame(root, height=30, width=100, bg='green')
        weather_node.pack(side=RIGHT, fill="x")

        # sunrise - sunset
        if int(time.strftime("%H")) > 12:
            sunrise_text = f'{weather.sunset:%H:%M}'
        else:
            sunrise_text = f'{weather.sunrise:%H:%M}'
        sunrise_image = Image.open('static/assets/Sunrise.png')
        sunrise_image = ImageTk.PhotoImage(sunrise_image.resize((30, 30), Image.LANCZOS))
        sunrise_node = tk.Label(weather_node, font=('Tahoma', 20), bg='green', fg='white',
                                padx=5, text=sunrise_text, compound=LEFT, image=sunrise_image)
        sunrise_node.image = sunrise_image
        sunrise_node.pack(in_=weather_node, anchor=E, side=LEFT)

        # wind dir and speed
        wind_text = self.directions[weather.wind_dir]
        wind_image = Image.open('static/assets/Wind.png')
        wind_image = ImageTk.PhotoImage(wind_image.resize((30, 30), Image.LANCZOS))
        wind_node = tk.Label(weather_node, font=('Tahoma', 20), bg='#007700', fg='white',
                             padx=5, text=wind_text, compound=LEFT, image=wind_image)
        wind_node.image = wind_image
        wind_node.pack(in_=weather_node, anchor=E, side=LEFT)

        #


if __name__ == '__main__':
    ss = SplashScreen()
    # NewsMethods().start()
    ss.increase(20)
    # load daemons
    time.sleep(0.5)
    ss.increase(20)
    time.sleep(0.5)
    ss.increase(20)
    time.sleep(0.5)
    ss.increase(20)
    time.sleep(0.5)
    ss.increase(20)
    time.sleep(0.5)
    ss.end()

    root_node = tk.Tk()
    root_node.bind('<Escape>', leave)
    # root_node.attributes("-fullscreen", True)
    root_node.configure(background='black')

    top_row = tk.Frame(root_node, bg='#550000')
    mid_row = tk.Frame(root_node, bg='#005500')
    bot_row = tk.Frame(root_node, bg='#000055', height=70)
    top_row.pack(side=TOP, fill="x", expand=False)
    mid_row.pack(side=TOP, fill="both", expand=True)
    bot_row.pack(side=BOTTOM, fill="x", expand=False)

    WeatherNode(top_row)
    clock = Clock(top_row)

    NewsNode(mid_row)

    while True:
        clock.hour_timer()
        clock.minutes_seconds_timer()
        clock.date()

        root_node.mainloop()

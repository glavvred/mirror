import sys
import tkinter as tk
from tkinter import *
import time

from news import NewsMethods
from settings import NEWS_COUNT
from weather import WeatherMethods


class Clock:
    days = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"]
    months = ["Января", "Февраля", "Марта", "Апреля", "Мая", "Июня", "Июля", "Августа", "Сентября",
              "Октября", "Ноября", "Декабря"]

    def __init__(self, root):
        clock_date_node = tk.Frame(root)
        clock_date_node.configure(background='blue')
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
        # splash screen
        startupscreen = tk.Tk()
        startupscreen.title('Mirror Mirror')
        welcometext = tk.Label(startupscreen, font=('arial', 40), bg='black', fg='white')
        startupscreen.configure(background='black')
        startupscreen.overrideredirect(True)
        welcometext.config(text='Hello dearest')
        welcometext.pack(side=LEFT, padx=120, pady=80)
        # Gets the requested values of the height and width.
        windowWidth = startupscreen.winfo_reqwidth()
        windowHeight = startupscreen.winfo_reqheight()
        # Gets both half the screen width/height and window width/height
        positionRight = int(startupscreen.winfo_screenwidth() / 3 - windowWidth / 2)
        positionDown = int(startupscreen.winfo_screenheight() / 2 - windowHeight / 2)

        # Positions the window in the center of the page.
        startupscreen.geometry("+{}+{}".format(positionRight, positionDown))
        startupscreen.update()
        # load daemons, display progressbar
        startupscreen.destroy()


class NewsNode:
    def __init__(self, root):
        news_node = tk.Frame(root)
        news_node.configure(background='black')
        news_node.pack(anchor=E, padx=15)

        news_widget = tk.Frame(news_node, height=NEWS_COUNT, width=100, bg='black')

        for article in NewsMethods.get_last(NEWS_COUNT):
            article_node = tk.Label(news_widget, font=('Tahoma', 10), bg='black', fg='white',
                                    text=article.title)
            article_node.pack(in_=news_widget, anchor=E, side=TOP)

        news_widget.pack()


def leave(event):
    root_node.destroy()
    sys.exit()


class WeatherNode:
    def __init__(self, root):
        weather = WeatherMethods.get_last()
        weather_node = tk.Frame(root, height=30, width=100, bg='green')
        weather_node.pack(side=RIGHT, fill="x")

        weather_widget = tk.Label(weather_node, bg='green', text='adasdasda sdasda'
                                                                 'asdasdasdasd'
                                                                 'asdasdasd\r\n'
                                                                 'asdasdasda'
                                                                 ''
                                                                 'asdasd\r\n'
                                                                 ''
                                                                 'asdasd'
                                                                 'asd ')
        weather_widget.pack()


if __name__ == '__main__':
    SplashScreen()

    root_node = tk.Tk()
    root_node.bind('<Escape>', leave)
    # root.attributes("-fullscreen", True)
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

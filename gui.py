import tkinter as tk
from tkinter import *
import time

from dbase.models import News
from settings import NEWS_COUNT

startupscreen = tk.Tk()
startupscreen.title('Mirror Mirror')
welcometext = tk.Label(startupscreen, font=('caviar dreams', 40), bg='black', fg='white')
startupscreen.configure(background='black')
startupscreen.overrideredirect(True)
welcometext.config(text='Hello dear')
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

global iteration
global timecount
global repull
global sleep

while True:

    def tick(time1=''):
        time2 = time.strftime("%H")
        if time2 != time1:
            time1 = time2
            clock_frame.config(text=time2)
        clock_frame.after(200, tick)


    def tock(time3=''):
        time4 = time.strftime(":%M:%S")
        if time4 != time3:
            time3 = time4
            clock_frame2.config(text=time4)
        clock_frame2.after(200, tock)


    root = tk.Tk()
    root.title('Mirror')

    masterclock = tk.Label(root)
    masterclock.pack(anchor=NW, fill=X, padx=45)
    masterclock.configure(background='black')
    clock_frame = tk.Label(root, font=('Courier', 70), bg='black', fg='white')
    clock_frame.pack(in_=masterclock, side=LEFT)
    clock_frame2 = tk.Label(root, font=('Courier', 70), bg='black', fg='white')
    clock_frame2.pack(in_=masterclock, side=LEFT, anchor=N, ipady=15)

    news_widget = tk.Text(root, height=NEWS_COUNT * 2, width=100, font=('Courier', 10), bg='black',
                          fg='white')
    news_widget.pack(side=RIGHT, anchor=E)

    for article in News.get_last(NEWS_COUNT):
        news_widget.insert(tk.END, article.title + "\r\n\r\n")

    tick()
    tock()

    # root.attributes("-fullscreen", True)
    root.configure(background='black')
    startupscreen.destroy()
    root.mainloop()

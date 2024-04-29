from tkinter import *

master = Tk()
def vscale_cb(value):
    print('vertical: {v}'.format(v=value))
def hscale_cb(value):
    print('horizontal: {v}'.format(v=value))

w = Scale(master, from_=0, to=100, command=vscale_cb)
w.pack()

w = Scale(master, from_=0, to=200, orient=HORIZONTAL, command=hscale_cb)
w.pack()

mainloop()
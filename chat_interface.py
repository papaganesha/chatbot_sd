#coding=utf-8


from tkinter import *

root = Tk()

def send():
    send = '<You> '+a.get()
    text.insert(END, '\n' + send)
    a.option_clear()
    #diggest message
text = Text(root, bg="white")
text.grid(row=0, column=0, columnspan=2)

a = Entry(root, width=80)

send = Button(root, text="Enviar", bg="white", width=20, command=send).grid(row=1, column=1)
a.grid(row=1, column=0)

root.title('PyBot')
root.mainloop()

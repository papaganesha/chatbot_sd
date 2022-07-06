import socket
import select
import sys
from tkinter import *

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
'''if len(sys.argv) != 3:
    print "Correct usage: script, IP address, port number"
    exit()'''
IP_address = str('localhost')
Port = int(50021)
server.connect((IP_address, Port))


root = Tk()
root.title('PyBot')
menubar = Menu(root)


def receive_and_return_server_msg():
    received_msg = server.recv(2048)
    return received_msg

def send():
    if a.get() != "":
        send = '<You> '+a.get()
        text.insert(END, '\n ' + send)
        server.send(a.get().encode())
        received_msg = receive_and_return_server_msg()
        if received_msg:
            print('1' + received_msg.decode())
            text.insert(END, '\n ' + received_msg.decode())
        a.delete(0, END)
    else:
        a.insert(0, 'Digite uma mensagem')

def clear():
    a.delete(0, END)


text = Text(root, bg="white")
text.grid(row=0, column=0, columnspan=3)
'''text.tag_add("highlight", "1.0", END)
text.tag_configure("highlight", foreground="green")'''



def clear_msgs():
    text.delete('1.0', END)

editmenu = Menu(menubar, tearoff=0)

editmenu.add_command(label="Limpar mensagens", command=clear_msgs)

menubar.add_cascade(label="Editar", menu=editmenu)


a = Entry(root, width=70)

send = Button(root, text="Enviar", bg="white", width=18, command=send).grid(row=1, column=1)
a.grid(row=1, column=0)

clear = Button(root, text="Limpar", bg="white", width=10, command=clear).grid(row=1, column=2)


received_msg = receive_and_return_server_msg()
print('1' + received_msg.decode())
text.insert(END, '\n ' + received_msg.decode())
root.config(menu=menubar)
root.mainloop()




'''input_message = input("")
print(f"<You> {input_message}")
server.send(input_message.encode())'''
'''sys.stdout.write("<You>")
sys.stdout.write(message)
sys.stdout.flush()'''


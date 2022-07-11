import socket
import select
import _thread
from tkinter import *
import sys
from cli_bot import initialize_and_return_trained_model, function_for_greetings

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
"""
the first argument AF_INET is the address domain of the socket. This is used when we have an Internet Domain
with any two hosts
The second argument is the type of socket. SOCK_STREAM means that data or characters are read in a continuous flow
"""
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
'''if len(sys.argv) != 3:
    print("Correct usage: script, IP address, port number")
    exit()'''
IP_address = str('localhost')
Port = int(50021)
server.bind((IP_address, Port)) 
#binds the server to an entered IP address and at the specified port number. The client must be aware of these parameters
server.listen(100)
#listens for 100 active connections. This number can be increased as per convenience
list_of_clients=[]


assistant = initialize_and_return_trained_model()

win = Tk()
win.title('PyBot Server')
menubar = Menu(win)

text = Text(win, bg="white")
text.grid(row=0, column=0, columnspan=3)


def clear_msgs():
    text.delete('1.0', END)

editmenu = Menu(menubar, tearoff=0)

editmenu.add_command(label="Limpar mensagens", command=clear_msgs)

menubar.add_cascade(label="Editar", menu=editmenu)

win.config(menu=menubar)




def clientthread(conn, addr, cont):
    welcome_msg = "<Pybot> Bem-vindo a esta sala de bate papo!".encode()
    conn.send(welcome_msg)
    #text.insert(END, '\n ' + welcome_msg)

    #sends a message to the client whose user object is conn
    while True:
            try:     
                message = conn.recv(2048)    
                if message:
                    print(f'< {addr[0]} > <{cont+1}> - ' + message.decode())
                    print(f"< localhost > - {assistant.request(message.decode())}")
                    message_to_send = f"<Pybot> {assistant.request(message.decode())}"
                    conn.send(message_to_send.encode())
                    #broadcast(message_to_send.encode(),conn)
                    #prints the message and address of the user who just sent the message on the server terminal
                else:
                    remove(conn)
            except:
                continue


def broadcast(message,connection):
    for client in list_of_clients:
        if client!=connection:
            try:
                client.send(message)
            except:
                client.close()
                remove(client)

def remove(connection):
    if connection in list_of_clients:
        list_of_clients.remove(connection)

cont = 0
#win.mainloop()
while True:
    conn, addr = server.accept()
    """
    Accepts a connection request and stores two parameters, conn which is a socket object for that user, and addr which contains
    the IP address of the client that just connected
    """
    list_of_clients.append(conn)
    print(f'< {addr[0]} >< {cont+1} > connected')
    #text.insert(END, '\n ' + f'< {addr[0]} >< {cont+1} > connected')

    #maintains a list of clients for ease of broadcasting a message to all available people in the chatroom
    #Prints the address of the person who just connected
    _thread.start_new_thread(clientthread,(conn,addr, cont))
    #creates and individual thread for every user that connects
    cont+=1


conn.close()
server.close()

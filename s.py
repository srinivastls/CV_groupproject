import socket
import cv2
import pickle
import struct
import tkinter as tk
from PIL import Image, ImageTk
import numpy as np
import threading
import pyshine as ps


IP = "172.17.4.252"
PORT = 1234
PORT1 = 1235
PORT2 = 1236
PORT3 = 1237
PORT4 = 1233
SIZE = 4096
FORMAT = "utf-8"
DISCONNECT_MSG = "BYE"


root = tk.Tk()
root.title("Video Chat")

# Create Canvas widgets for displaying video streams
canvas1 = tk.Canvas(root, width=500, height=480)
canvas1.pack(side="left")

canvas2 = tk.Canvas(root, width=500, height=480)
canvas2.pack(side="right")


# for video
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((IP, PORT))

# for recv messages
client_socket1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket1.connect((IP, PORT1))


# for recev file
client_socket3 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket3.connect((IP, PORT3))

# for recev audio
client_socket4 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket4.connect((IP, PORT4))

mode = 'send'
name = 'CLIENT Sending AUDIO'
mode1 = 'get'
name1 = 'CLIENT RECEIVING AUDIO'


def receive_messages():
    while True:
        try:
            msg = client_socket1.recv(SIZE).decode(FORMAT)
            if msg == DISCONNECT_MSG:
                print("[Server] Disconnected.")
                break
            print(f"[Client] {msg}")
        except ConnectionAbortedError:
            print("[Server] Connection was aborted by the server.")
            break


def audio_streaming():
    # print("audio")
    data = b""
    payload_size = struct.calcsize("Q")
    audio, context = ps.audioCapture(mode=mode)
    # ps.showPlot(context1,name1)
    if client_socket4:
        while True:

            frame = audio.get()

            a = pickle.dumps(frame)
            message = struct.pack("Q", len(a))+a
            client_socket4.sendall(message)


def receive_audio():
    data = b""
    payload_size = struct.calcsize("Q")
    audio1, context1 = ps.audioCapture(mode=mode1)
    while True:
        try:
            while len(data) < payload_size:
                packet = client_socket4.recv(8192)  # 4K
                if not packet:
                    break
                data += packet
            packed_msg_size = data[:payload_size]
            data = data[payload_size:]
            msg_size = struct.unpack("Q", packed_msg_size)[0]

            while len(data) < msg_size:
                data += client_socket4.recv(8192)
            frame_data = data[:msg_size]
            data = data[msg_size:]
            audio1.put(frame)
        except:
            print("Bye")
        frame = pickle.loads(frame_data)


def video_streaming():
    data = b""
    payload_size = struct.calcsize("Q")

    while True:
        if client_socket:
            cap = cv2.VideoCapture(0)
            while (cap.isOpened()):
                img, frame = cap.read()
                a = pickle.dumps(frame)
                message = struct.pack("Q", len(a)) + a
                client_socket.sendall(message)

                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                photo = ImageTk.PhotoImage(image=Image.fromarray(frame))
                canvas1.create_image(0, 0, anchor=tk.NW, image=photo)
                canvas1.update()


def receive_frames():
    data = b""
    payload_size = struct.calcsize("Q")
    frame_data = None

    while True:
        try:
            while len(data) < payload_size:
                packet = client_socket.recv(4096)  # Increase buffer size
                if not packet:
                    break
                data += packet

            packed_msg = data[:payload_size]
            data = data[payload_size:]
            msg_size = struct.unpack("Q", packed_msg)[0]

            while len(data) < msg_size:
                data += client_socket.recv(4096)  # Increase buffer size
            frame_data = data[:msg_size]
            data = data[msg_size:]

        except Exception as e:
            print("Error:", e)
            break

        vid = pickle.loads(frame_data)

        # Update the canvas with the received frame
        vid = cv2.cvtColor(vid, cv2.COLOR_BGR2RGB)
        photo = ImageTk.PhotoImage(image=Image.fromarray(vid))
        canvas2.create_image(0, 0, anchor=tk.NW, image=photo)
        canvas2.update()





def send_file(client, file_path):
    with open(file_path, "rb") as file:
        while True:
            data = file.read(SIZE)
            # print(len(data))
            if not data:
                break
            client.send(data)
    client.send(b"")  # Signal the end of the file


def recevive_File():
    while True:
        print("Waiting for File ........")
        filename = client_socket3.recv(SIZE).decode(FORMAT)
        if not filename:
            break
        print(filename)
        with open(filename, "wb") as file:
            while True:
                data = client_socket3.recv(SIZE)
                print(len(data))
                if len(data) < 4096:
                    file.write(data)
                    break
                file.write(data)
        print("File Received")


def to_chat():
    while True:
        msg = input("> ")
        if (msg == "-1"):
            break
        client_socket1.send(msg.encode(FORMAT))


def to_send_file():
    client_socket2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket2.connect((IP, PORT2))
    FILENAME = input(
        "Enter the files name to send with extension (For ex: sample.txt) or for receiving Enter -1: ")
    print(FILENAME)
    client_socket2.send(FILENAME.encode(FORMAT))
    msg = client_socket2.recv(SIZE).decode(FORMAT)
    no = input(msg)
    client_socket2.send(no.encode(FORMAT))
    send_file(client_socket2, FILENAME)
    print("hello")
    client_socket2.close()
    
def main1():
    
    while True:

        print("1.To Chat\n 2.To Send File")
        option = int(input("Enter here:"))
        if option == 1:
            to_chat()
        else:
            to_send_file()

# Start a new thread for receiving chat messages
chat_thread = threading.Thread(target=receive_messages)
chat_thread.start()


# Start a new thread for video streaming
video_thread = threading.Thread(target=video_streaming)
video_thread.start()

# Start a new thread for receving files
file_recevie_thread = threading.Thread(target=recevive_File)
file_recevie_thread.start()

# Start a new thread for receving audio
#audio_thread = threading.Thread(target=audio_streaming)
#audio_thread.start()

#start main thread
main_thread=threading.Thread(target=main1)
main_thread.start()


# Create a separate thread for receiving frames
receive_thread = threading.Thread(target=receive_frames)
receive_thread.start()


#receive_audo = threading.Thread(target=receive_audio)
#receive_audo.start()



    



root.mainloop()
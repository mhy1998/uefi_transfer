import tkinter as tk
from tkinterdnd2 import DND_FILES, TkinterDnD
import socket
import threading
from tkinter import filedialog
import tkinter.messagebox as messagebox
import os

class ServerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Server")
        
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.SERVER_HOST = '127.0.0.1'
        self.SERVER_PORT = 4000

        # Server label
        self.server_label = tk.Label(root, text="Server", font=("Helvetica", 16, "bold"))
        self.server_label.pack()

        # Connection status label
        self.connection_label = tk.Label(root, text="Waiting for connection...", font=("Helvetica", 12))
        self.connection_label.pack()

        # Message entry
        self.server_entry = tk.Entry(root, width=50)
        self.server_entry.pack(pady=5)

        # Send button
        self.send_button = tk.Button(root, text="Send", command=self.send_message)
        self.send_button.pack()

        # Message listbox
        self.message_listbox = tk.Listbox(root, width=60, height=15)
        self.message_listbox.pack(pady=10)

        # IP label
        self.ip_label = tk.Label(root, text="", font=("Helvetica", 10))
        self.ip_label.pack()

        # Start server button
        self.start_server_button = tk.Button(root, text="Start Server", command=self.start_server, bg="#4CAF50", fg="white")
        self.start_server_button.pack(pady=10)

        self.input_frame = tk.Frame(root)
        self.input_frame.pack(pady=10)

        self.send_button = tk.Button(self.input_frame, text="Send filename", command=self.send_filename)
        self.send_button.pack(side=tk.TOP)
        self.send_button = tk.Button(self.input_frame, text="Send filesize", command=self.send_filesize)
        self.send_button.pack(side=tk.TOP)
        self.send_button = tk.Button(self.input_frame, text="Send filedata", command=self.sendfile)
        self.send_button.pack(side=tk.TOP)

        # TkinterDnD for drag and drop functionality
        self.root.drop_target_register(DND_FILES)
        self.root.dnd_bind('<<Drop>>', self.drop_event)

        # Instructions
        self.instructions_label = tk.Label(root, text="Drag and drop files here or click 'Send File' to choose.")
        self.instructions_label.pack(pady=5)

    def start_server(self):
        self.server_socket.bind((self.SERVER_HOST, self.SERVER_PORT))
        self.server_socket.listen(1)
        
        self.connection_label.config(text="Waiting for connection...")
        self.client_socket, self.client_address = self.server_socket.accept()
        self.connection_label.config(text="Connected to: " + self.client_address[0])
        self.ip_label.config(text="Client IP: " + self.client_address[0])
        
        #threading.Thread(target=self.receive_message, daemon=True).start()
        #threading.Thread(target=self.receive_file, daemon=True).start()

        threading.Thread(target=self.receivefilemhy, daemon=True).start()

    def drop_event(self, event):
        self.filepath = event.data
        self.filename = self.filepath.split("/")[-1]
        self.filenamelegth = str(len(self.filename))
        self.filesize = os.path.getsize(self.filepath)
        self.message_listbox.insert(tk.END, "Server: " + self.filepath)
        print(self.filepath)
        print(self.filename)
        print(self.filenamelegth)
        print(self.filesize)

    def send_filename(self):

        try:
            print("send_filename ")
            print(self.filename)
            filename_bytes = self.filename.encode('utf-8')
            print(self.filename)
            self.client_socket.sendall(filename_bytes)
            self.message_listbox.insert(tk.END, "send_filename: " + self.filename)
        except Exception as e:
            print("Error:", e)

    def send_filesize(self):
        try:
            print("send_filesize ")
            print(self.filesize)
            self.client_socket.sendall(str(self.filesize).encode('utf-8'))
            self.message_listbox.insert(tk.END, "send_filesize: " + str(self.filesize))
        except Exception as e:
            print("Error:", e)
            
    def sendfile(self):

        try:
            print("sendfile data")
            with open(self.filepath, 'rb') as file:
                file_data = file.read()
                self.client_socket.sendall(file_data)
            # with open(self.filepath, 'rb') as f:
            #     while True:
            #         data = f.read(1024)
            #         if not data:
            #             break
            #         self.client_socket.sendall(data)
            print("sendfile data success")
            self.message_listbox.insert(tk.END, "sendfile data success")
        except Exception as e:
            print("Error:", e)

    def receivefilemhy(self):
        while True:
            try:
                # #1.
                # filenamelen = int(self.client_socket.recv(1).decode('utf-8'))
                # print("filenamelen %d\n",filenamelen)
                #2.
                filename = self.client_socket.recv(1024).decode('utf-8')
                print(filename)
                print('\n')
                #3.
                filesize = int(self.client_socket.recv(30).decode('utf-8'))
                print(filesize)
                print('\n')
                #4. 接收数据并写入文件
                file_path = os.path.join("D:/", filename)
                with open(file_path, 'wb') as f:
                    total_received = 0
                    while total_received < filesize:
                        data = self.client_socket.recv(1024)
                        total_received += len(data)
                        f.write(data)
                print("File received successfully")
            except Exception as e:
                print("Error:", e)

    def receive_file(self):
        while True:
            try:
                # 接收文件名
                filename_bytes = b''
                while True:
                    byte = self.client_socket.recv(1)
                    if byte == b'|':
                        break
                    filename_bytes += byte
                filename = filename_bytes.decode('utf-8')
                print(filename)
                # 接收文件大小
                filesize_bytes = b''
                while True:
                    byte = self.client_socket.recv(1)
                    if byte == b'|':
                        break
                    filesize_bytes += byte
                filesize = int(filesize_bytes.decode('utf-8'))
                print(filesize)
                # 接收数据并写入文件
                file_path = os.path.join("D:/", filename)
                with open(file_path, 'wb') as f:
                    total_received = 0
                    while total_received < filesize:
                        data = self.client_socket.recv(1024)
                        total_received += len(data)
                        f.write(data)
                print("File received successfully")
            except Exception as e:
                print("Error:", e)

    def receive_message(self):
        while True:
            message = self.client_socket.recv(1024).decode('utf-8')
            print(message[0:5])
            if message:
                if message.startswith("File:"):
                    filename = message[5:].split("###")[0]
                    file_data = b''
                    file_data += message.split('###')[1].encode('utf-8')
                    print("receive filename:")
                    print(filename)
                    print(file_data)
                    while True:
                        try:
                            print(1)
                            self.client_socket.settimeout(5)
                            data = self.client_socket.recv(1024)

                            # if b'###' in data:
                            #     file_data += data.split(b'###')[1]
                            #     break
                            if not data:
                                break
                            file_data += data
                        except socket.timeout:
                            break
                    file_path = os.path.join("D:/", filename)
                    print(file_path)
                    with open(file_path, 'wb') as file:
                        file.write(file_data)
                    self.message_listbox.insert(tk.END, "Server: File received and saved to D:/")
                else:
                    self.message_listbox.insert(tk.END, "Client: " + message)

    def send_message(self):
        message = self.server_entry.get()
        if message:
            self.client_socket.send(message.encode('utf-8'))
            self.message_listbox.insert(tk.END, "Server: " + message)
            self.server_entry.delete(0, tk.END)

if __name__ == "__main__":
    root = TkinterDnD.Tk()
    server_gui = ServerGUI(root)
    root.mainloop()


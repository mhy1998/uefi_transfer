import tkinter as tk
from tkinterdnd2 import DND_FILES, TkinterDnD
import socket
import threading
from tkinter import filedialog
import tkinter.messagebox as messagebox
import os
import time

class ClientGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Socket Client")
        self.root.geometry("500x600")

        # self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # self.client_socket.setblocking(False) 
        # self.SERVER_HOST = '192.168.77.30'
        # #self.SERVER_HOST = '127.0.0.1'
        # self.SERVER_PORT = 4000

        # Frame for input and send area
        self.input_frame = tk.Frame(root)
        self.input_frame.pack(pady=10)

        # self.client_label = tk.Label(self.input_frame, text="Message:")
        # self.client_label.pack(side=tk.LEFT)

        # self.client_entry = tk.Entry(self.input_frame, width=40)
        # self.client_entry.pack(side=tk.LEFT, padx=5)

        # self.send_file_button = tk.Button(self.input_frame, text="Send File", command=self.send_file2)
        # self.send_file_button.pack(side=tk.LEFT)

        # self.send_button = tk.Button(self.input_frame, text="Send", command=self.send_message)
        # self.send_button.pack(side=tk.LEFT)

        # self.choose_file_button = tk.Button(self.input_frame, text="choose File", command=self.choose_file)
        # self.choose_file_button.pack(side=tk.LEFT)

        # self.send_button = tk.Button(self.input_frame, text="Send filenamelen", command=self.send_filenamelen)
        # self.send_button.pack(side=tk.TOP)
        self.send_button = tk.Button(self.input_frame, text="Send filename", command=self.send_filename)
        self.send_button.pack(side=tk.TOP)
        self.send_button = tk.Button(self.input_frame, text="Send filesize", command=self.send_filesize)
        self.send_button.pack(side=tk.TOP)
        self.send_button = tk.Button(self.input_frame, text="Send filedata", command=self.sendfile)
        self.send_button.pack(side=tk.TOP)

        # Chat display area
        self.message_listbox = tk.Listbox(root, width=60, height=15)
        self.message_listbox.pack(pady=10)

        # Server IP display
        self.ip_label = tk.Label(root, text="")
        self.ip_label.pack()

        # Start client button
        self.start_client_button = tk.Button(root, text="Connect to Server", command=self.start_client)
        self.start_client_button.pack(pady=5)
        self.start_client_button = tk.Button(root, text="receive  file", command=self.receive_file)
        self.start_client_button.pack(pady=5)
        # self.start_client_button = tk.Button(root, text="Close Client", command=self.close_client)
        # self.start_client_button.pack(pady=5)

        # TkinterDnD for drag and drop functionality
        self.root.drop_target_register(DND_FILES)
        self.root.dnd_bind('<<Drop>>', self.drop_event)

        # Instructions
        self.instructions_label = tk.Label(root, text="Drag and drop files here or click 'Send File' to choose.")
        self.instructions_label.pack(pady=5)

    def close_client(self):
        # 创建一个新的 Socket 连接
        # client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        try:
            self.client_socket.close()
            # self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # self.client_socket.connect((self.SERVER_HOST, self.SERVER_PORT))
            # self.ip_label.config(text="Connected to: " + self.SERVER_HOST)
            # threading.Thread(target=self.receive_message, daemon=True).start()
            # self.ip_label.config(text="Connected to: " + self.SERVER_HOST)
        except self.client_socket.error as e:
            print(f"关闭套接字时发生错误：{e}")
            
    def start_client(self):
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            #self.client_socket.setblocking(False)
            self.SERVER_HOST = '192.168.77.30'
            #self.SERVER_HOST = '127.0.0.1'
            self.SERVER_PORT = 4000
            self.client_socket.connect((self.SERVER_HOST, self.SERVER_PORT))
            # threading.Thread(target=self.receive_message, daemon=True).start()
            self.ip_label.config(text="Connected to: " + self.SERVER_HOST)
            # threading.Thread(target=self.receive_file, daemon=True).start()

        except ConnectionRefusedError:
            messagebox.showerror("Connection Error", "Failed to connect to the server.")

    def receive_message(self):
        while True:
            try:
                message = self.client_socket.recv(1024).decode('utf-8')
                if message:
                    self.message_listbox.insert(tk.END, "Server: " + message)
            except ConnectionResetError:
                messagebox.showerror("Connection Error", "Connection to the server was lost.")
                self.client_socket.close()
                break

    def send_message(self):
        message = self.client_entry.get()
        if message:
            try:
                self.client_socket.send(message.encode('utf-8'))
                self.message_listbox.insert(tk.END, "Client: " + message)
                self.client_entry.delete(0, tk.END)
            except socket.error:
                messagebox.showerror("Connection Error", "Failed to send message to the server.")
                self.client_socket.close()

    def choose_file(self):
        self.filepath = filedialog.askopenfilename()
        self.filename = self.filepath.split("/")[-1]
        self.filenamelegth = str(len(self.filename))
        self.filesize = os.path.getsize(self.filepath)
        self.message_listbox.insert(tk.END, "Client: " + self.filepath)
        print(self.filepath)
        print(self.filename)
        print(self.filenamelegth)
        print(self.filesize)
        #if filepath:
            #self.send_file(filepath)

    def drop_event(self, event):
        self.filepath = event.data
        self.filename = self.filepath.split("/")[-1]
        self.filenamelegth = str(len(self.filename))
        self.filesize = os.path.getsize(self.filepath)
        self.message_listbox.insert(tk.END, "Client: " + self.filepath)
        print(self.filepath)
        print(self.filename)
        print(self.filenamelegth)
        print(self.filesize)

    def send_file(self):
        if self.filepath:
            try:
                filename = self.filepath.split("/")[-1]
                with open(self.filepath, 'rb') as file:
                    file_data = file.read()
                self.client_socket.sendall(f"File:{filename}".encode('utf-8') + b'###' + file_data)
                self.message_listbox.insert(tk.END, "Client: File sent")
            except (FileNotFoundError, PermissionError):
                messagebox.showerror("File Error", "Failed to open or send the selected file.")
            except socket.error:
                messagebox.showerror("Connection Error", "Failed to send file to the server.")
                self.client_socket.close()
    def send_file2(self):
        # 发送文件名长度、文件名和文件大小信息
        # self.client_socket.send("File:".encode('utf-8'))
        # self.client_socket.send(self.filenamelegth.encode('utf-8'))
        # self.client_socket.send(self.filename.encode('utf-8'))
        # self.client_socket.send(self.filesize.encode('utf-8'))

        # 发送文件内容
        try:
            # 发送文件名和文件大小
            print("send")
            filename_bytes = self.filename.encode('utf-8')
            print(self.filename)
            self.client_socket.sendall(filename_bytes)
            self.client_socket.sendall(b'|')
            print(self.filesize)
            self.client_socket.sendall(str(self.filesize).encode('utf-8'))
            self.client_socket.sendall(b'|')
            
            # 打开文件并发送数据
            with open(self.filepath, 'rb') as f:
                while True:
                    data = f.read(1024)
                    if not data:
                        break
                    self.client_socket.sendall(data)
            print("File sent successfully")
        except Exception as e:
            print("Error:", e)


    def send_filenamelen(self):

        try:
            print("send_filenamelen ")
            print(self.filenamelegth)
            filename_bytes = self.filenamelegth.encode('utf-8')
            print(self.filename)
            self.client_socket.sendall(filename_bytes)
            self.message_listbox.insert(tk.END, "send_filenamelen: " + self.filenamelegth)
        except Exception as e:
            print("Error:", e)

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

    def receive_file(self):
        try:
            # 接收文件名
            filename_bytes = b''
            while True:
                byte = self.client_socket.recv(1)

                if byte == b'|':
                    break
                filename_bytes += byte
            filename = filename_bytes.decode('utf-8')
            self.message_listbox.insert(tk.END, "receive filename: " + filename)
            # 接收文件大小
            filesize_bytes = b''
            while True:
                byte = self.client_socket.recv(1)
                if byte == b'|':
                    break
                filesize_bytes += byte
            filesize = int(filesize_bytes.decode('utf-8'))
            self.message_listbox.insert(tk.END, "receive filesize: " + str(filesize))
            # 接收数据并写入文件
            file_path = os.path.join("D:/", filename)
            with open(file_path, 'wb') as f:
                total_received = 0
                while total_received < filesize:
                    data = self.client_socket.recv(1024)
                    total_received += len(data)
                    f.write(data)
            self.message_listbox.insert(tk.END, "File received at "+ file_path)
        except Exception as e:
            print("Error:", e)

if __name__ == "__main__":
    root = TkinterDnD.Tk()
    client_gui = ClientGUI(root)
    root.mainloop()

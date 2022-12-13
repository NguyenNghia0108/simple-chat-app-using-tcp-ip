import os
import socket
import threading
import tkinter
import tkinter.scrolledtext
from tkinter import simpledialog

HOST = socket.gethostbyname("127.0.0.1")
PORT = 2207

key = 7943


class Client:
    def __init__(self, host, port):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((host, port))

        msg = tkinter.Tk()
        msg.withdraw()

        self.nickname = ''
        while self.nickname == '':
            self.nickname = simpledialog.askstring("Nickname", "Nhập tên người dùng", parent=msg)

        self.gui_done = False
        self.running = True

        gui_thread = threading.Thread(target=self.gui_loop)
        receive_thread = threading.Thread(target=self.receive)

        gui_thread.start()
        receive_thread.start()

    def gui_loop(self):
        self.win = tkinter.Tk()
        self.win.title("CHAT")
        self.win.configure(bg="snow")

        self.win.columnconfigure(0, weight=1)
        self.win.rowconfigure(1, weight=1)

        self.nickname_label = tkinter.Label(self.win, text="Tên đăng nhập: " + self.nickname, bg="snow")
        self.nickname_label.config(font=('Calibri', 16, "bold"))
        self.nickname_label.grid(column=0, row=0, padx=2, pady=2, sticky='nsew')

        self.text_area_label = tkinter.Label(self.win, text="Trò chuyện:", bg="snow")
        self.text_area_label.config(font=('Calibri', 16, "bold"))
        self.text_area_label.grid(column=0, row=1, padx=2, pady=2, sticky='nsew')

        self.text_area = tkinter.scrolledtext.ScrolledText(self.win, width=50, bg="snow")
        self.text_area.grid(column=0, row=2, padx=5, pady=5, sticky='nsew')
        self.text_area.config(state="disabled", font=('Calibri', 16,))

        self.ca_label = tkinter.Label(self.win, text="Đang trực tuyến:", bg="snow")
        self.ca_label.config(font=('Calibri', 16, "bold"))
        self.ca_label.grid(column=1, row=0, padx=5, pady=5, sticky='nsew')

        self.clients_area = tkinter.Text(self.win, width=20, bg="snow")
        self.clients_area.grid(column=1, row=1, rowspan=5, padx=5, pady=5, sticky='nsew')
        self.clients_area.config(state="disabled", font=('Calibri', 16))

        self.msg_label = tkinter.Label(self.win, text="Lời nhắn:", bg="snow")
        self.msg_label.config(font=('Calibri', 18, "bold"))
        self.msg_label.grid(column=0, row=3, padx=5, pady=5, sticky='nsew')

        self.input_area = tkinter.Text(self.win, width=55, height=5, bg="snow")
        self.input_area.config(font=('Calibri', 15))
        self.input_area.grid(column=0, row=4, padx=5, pady=5, sticky='nsew')

        self.send_button = tkinter.Button(self.win, text="Gửi", command=self.write)
        self.send_button.config(font=('Calibri', 14))
        self.send_button.grid(column=0, row=5, padx=5, pady=5, sticky='nsew')

        self.file_button = tkinter.Button(self.win, text="Gửi file", command=self.select_file)
        self.file_button.config(font=('Calibri', 14))
        self.file_button.grid(column=0, row=6, padx=5, pady=5, sticky='nsew')

        self.gui_done = True

        self.win.protocol("WM_DELETE_WINDOW", self.stop)

        self.win.mainloop()

    def write(self):
        message = self.input_area.get('1.0', 'end')

        crypt = ""
        for i in message:
            crypt += chr(ord(i) ^ key)

        crypt_message = f"{self.nickname}: {crypt}"

        if self.input_area.get('1.0', 'end-1c') != "":
            self.sock.send(crypt_message.encode('utf-8'))
            self.input_area.delete('1.0', 'end')
            self.clients_area.delete('1.0', 'end')

    def stop(self):
        self.running = False
        self.win.destroy()
        self.sock.close()
        exit(0)

    def receive(self):
        while self.running:
            if self.gui_done:
                try:
                    message = self.sock.recv(1024).decode("utf-8")
                    if message == 'NICK':
                        self.sock.send(self.nickname.encode('utf-8'))
                    elif '[USERS]' in message:
                        clients_list = message[7:]
                        self.clients_area.config(state="normal")
                        self.clients_area.delete('1.0', 'end')
                        self.clients_area.insert('end', clients_list)
                        self.clients_area.yview('end')
                        self.clients_area.config(state="disabled")
                    else:
                        decrypt_message = ""
                        k = False
                        for i in message:
                            if i == ":":
                                k = True
                                decrypt_message += i
                            elif k == False or i == " ":
                                decrypt_message += i
                            else:
                                decrypt_message += chr(ord(i) ^ key)

                        self.text_area.config(state="normal")

                        self.text_area.insert('end', decrypt_message)
                        self.text_area.yview('end')
                        self.text_area.config(state="disabled")
                except ConnectionAbortedError:
                    break
                except:
                    print("Error")
                    self.sock.close()
                    self.stop()
                    break
    def select_file(self):
        filename=filedialog.aslopenfilename(initialdir=os.getcwd(),
                                            title="Select file name",
                                            filetype=(('file_type,"*.txt'),("all files","*.*")))

if __name__ == '__main__':
    client = Client(HOST, PORT)

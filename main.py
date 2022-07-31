from datetime import datetime
from multiprocessing import Process, Queue
from queue import Empty
from tkinter import Button, Tk, Frame, BOTH, LEFT, Entry, StringVar, Text, END
from typing import Optional

from DummyDataInOut import DummyDataInOut


class LongRunningTask(Process):

    def __init__(self, input_queue: "Queue[str]", ouput_queue: "Queue[str]"):
        super().__init__()
        self.input_queue = input_queue
        self.output_queue = ouput_queue
        self.data_gen = DummyDataInOut()

    def run(self):
        stop = False
        while not stop:
            if self.input_queue.empty():
                self.output_queue.put(self.data_gen.get_data())
            else:
                print(f"{datetime.now():%H:%M:%S.%f} Got command")
                command = self.input_queue.get()
                if command == "stop":
                    stop = True
                else:
                    self.output_queue.put(self.data_gen.accept_command(command))


class MainWindow(Tk):

    def __init__(self):
        super().__init__()

        self.output_text = None
        self.start_stop_button = None
        self.command_button = None
        self.helper_process: Optional[Process] = None
        self.input_queue: "Queue[str]" = Queue()
        self.output_queue: "Queue[str]" = Queue()

        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.geometry('400x500')
        self.input_text = StringVar()

        self.build_interface()

        self.running = False

    def build_interface(self):
        frame = Frame()
        frame.pack(fill=BOTH, side=LEFT, expand=True)
        label = Entry(master=frame, textvariable=self.input_text)
        label.pack(padx=10, pady=10)
        self.command_button = Button(frame, text="Send command", command=self.send_command)
        self.command_button.pack(padx=10, pady=10)
        self.start_stop_button = Button(frame, text="Start", command=self.toggle_process)
        self.start_stop_button.pack(padx=10, pady=10)
        self.output_text = Text(frame, height=20, width=50)
        self.output_text.pack(padx=10, pady=10)

    def update_text_field(self):
        if self.helper_process.is_alive():
            try:
                next_text = self.output_queue.get(block=False)
                self.output_text.insert(END, f"{next_text}\n")
            except Empty:
                pass
            self.after(300, self.update_text_field)
        else:
            self.start_stop_button["text"] = "Start"
            self.running = False

    def send_command(self):
        print(f"{datetime.now():%H:%M:%S.%f} Send commmand.")
        self.input_queue.put(self.input_text.get())

    def toggle_process(self):
        if self.running:
            self.input_queue.put("stop")
        else:
            self.running = True
            self.after(300, self.update_text_field)
            self.start_stop_button["text"] = "Stop"
            self.helper_process = LongRunningTask(self.input_queue, self.output_queue)
            self.helper_process.start()

    def on_closing(self):
        self.input_queue.put("stop")
        try:
            self.helper_process.join()
        except AttributeError:
            pass
        self.destroy()


if __name__ == '__main__':
    root = MainWindow()
    root.mainloop()

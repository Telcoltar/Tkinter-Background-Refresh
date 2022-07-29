import time
from multiprocessing import Process, Queue
from queue import Empty
from tkinter import Button, Tk, Frame, Label, BOTH, LEFT, Entry, StringVar, Text, END


class LongRunningTask(Process):

    def __init__(self, input_queue: "Queue[str]", ouput_queue: "Queue[str]"):
        super().__init__()
        self.input_queue = input_queue
        self.output_queue = ouput_queue

    def run(self):
        next_input = self.input_queue.get()
        while next_input != "stop":
            number = int(next_input)
            self.output_queue.put("Beginn calculation")
            time.sleep(3)
            result = number ** 2
            self.output_queue.put("Still processing")
            time.sleep(3)
            self.output_queue.put(f"Result: {result}")
            next_input = self.input_queue.get()
        print("End")


class MainWindow(Tk):

    def __init__(self):
        super().__init__()

        self.input_queue: "Queue[str]" = Queue()
        self.output_queue: "Queue[str]" = Queue()
        self.helper_process = LongRunningTask(self.input_queue, self.output_queue)
        self.helper_process.start()

        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.geometry('200x300')
        self.input_text = StringVar()

        frame = Frame()
        frame.pack(fill=BOTH, side=LEFT, expand=True)
        label = Entry(master=frame, textvariable=self.input_text)
        label.pack(padx=10, pady=10)
        button = Button(frame, text="Calculate", command=self.calculate)
        button.pack(padx=10, pady=10)
        self.output_text = Text(frame, height=10, width=40)
        self.output_text.pack(padx=10, pady=10)

        self.after(300, self.update_text_field)

    def update_text_field(self):
        try:
            next_text = self.output_queue.get(block=False)
            self.output_text.insert(END, f"{next_text}\n")
        except Empty:
            pass
        self.after(300, self.update_text_field)

    def calculate(self):
        print("Calculate")
        self.input_queue.put(self.input_text.get())

    def on_closing(self):
        self.input_queue.put("stop")
        self.helper_process.join()
        self.destroy()


if __name__ == '__main__':
    root = MainWindow()
    root.mainloop()

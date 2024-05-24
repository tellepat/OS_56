import threading
import random
import string
import time
import tkinter as tk
from tkinter import scrolledtext, ttk

class Monitor:
    def __init__(self):
        self.lock = threading.Condition()
        self.buffer = []

    def produce(self, item):
        with self.lock:
            self.buffer.append(item)
            self.lock.notify()

    def consume(self):
        with self.lock:
            while not self.buffer:
                self.lock.wait()
            item = self.buffer.pop(0)
            return item

def producer(monitor, text_widget, produced_str_widget, speed_var, running_event, produced_string):
    while running_event.is_set():
        time.sleep(speed_var.get())
        char = random.choice(string.ascii_letters + string.digits + string.punctuation)
        monitor.produce(char)
        text_widget.insert(tk.END, f'Produced: {char}\n')
        text_widget.see(tk.END)
        produced_string.append(char)
        produced_str_widget.delete('1.0', tk.END)
        produced_str_widget.insert(tk.END, ''.join(produced_string))

def consumer(monitor, text_widget, consumed_str_widget, speed_var, running_event, consumed_string):
    while running_event.is_set():
        item = monitor.consume()
        if not item.isalpha():
            text_widget.insert(tk.END, f'Consumed (removed): {item}\n')
        else:
            text_widget.insert(tk.END, f'Consumed (kept): {item}\n')
            consumed_string.append(item)
            consumed_str_widget.delete('1.0', tk.END)
            consumed_str_widget.insert(tk.END, ''.join(consumed_string))
        text_widget.see(tk.END)
        time.sleep(speed_var.get())

def start_producer(monitor, prod_text_widget, prod_str_widget, speed_var, prod_event, produced_string):
    if not prod_event.is_set():
        prod_event.set()
        threading.Thread(target=producer, args=(monitor, prod_text_widget, prod_str_widget, speed_var, prod_event, produced_string), daemon=True).start()

def stop_producer(prod_event):
    prod_event.clear()

def start_consumer(monitor, cons_text_widget, cons_str_widget, speed_var, cons_event, consumed_string):
    if not cons_event.is_set():
        cons_event.set()
        threading.Thread(target=consumer, args=(monitor, cons_text_widget, cons_str_widget, speed_var, cons_event, consumed_string), daemon=True).start()

def stop_consumer(cons_event):
    cons_event.clear()

def main():
    root = tk.Tk()
    root.title("Producer-Consumer with Monitor")

    frame = tk.Frame(root)
    frame.pack(padx=10, pady=10)

    prod_label = tk.Label(frame, text="Producer Output")
    prod_label.grid(row=0, column=0, padx=5, pady=5)
    prod_text_widget = scrolledtext.ScrolledText(frame, width=50, height=10)
    prod_text_widget.grid(row=1, column=0, padx=5, pady=5)

    cons_label = tk.Label(frame, text="Consumer Output")
    cons_label.grid(row=0, column=1, padx=5, pady=5)
    cons_text_widget = scrolledtext.ScrolledText(frame, width=50, height=10)
    cons_text_widget.grid(row=1, column=1, padx=5, pady=5)

    prod_str_label = tk.Label(frame, text="Produced String")
    prod_str_label.grid(row=2, column=0, padx=5, pady=5)
    prod_str_widget = scrolledtext.ScrolledText(frame, width=50, height=5)
    prod_str_widget.grid(row=3, column=0, padx=5, pady=5)

    cons_str_label = tk.Label(frame, text="Consumed String")
    cons_str_label.grid(row=2, column=1, padx=5, pady=5)
    cons_str_widget = scrolledtext.ScrolledText(frame, width=50, height=5)
    cons_str_widget.grid(row=3, column=1, padx=5, pady=5)

    speed_var_prod = tk.DoubleVar(value=1.0)
    speed_var_cons = tk.DoubleVar(value=1.0)

    speed_label_prod = tk.Label(frame, text="Producer Speed (seconds)")
    speed_label_prod.grid(row=4, column=0, padx=5, pady=5)
    speed_slider_prod = ttk.Scale(frame, from_=0.1, to=2.0, orient="horizontal", variable=speed_var_prod, length=200)
    speed_slider_prod.grid(row=5, column=0, padx=5, pady=5)

    speed_label_cons = tk.Label(frame, text="Consumer Speed (seconds)")
    speed_label_cons.grid(row=4, column=1, padx=5, pady=5)
    speed_slider_cons = ttk.Scale(frame, from_=0.1, to=2.0, orient="horizontal", variable=speed_var_cons, length=200)
    speed_slider_cons.grid(row=5, column=1, padx=5, pady=5)

    monitor = Monitor()
    prod_event = threading.Event()
    cons_event = threading.Event()

    produced_string = []
    consumed_string = []

    start_prod_button = tk.Button(frame, text="Start Producer", command=lambda: start_producer(monitor, prod_text_widget, prod_str_widget, speed_var_prod, prod_event, produced_string))
    start_prod_button.grid(row=6, column=0, padx=5, pady=5)

    stop_prod_button = tk.Button(frame, text="Stop Producer", command=lambda: stop_producer(prod_event))
    stop_prod_button.grid(row=7, column=0, padx=5, pady=5)

    start_cons_button = tk.Button(frame, text="Start Consumer", command=lambda: start_consumer(monitor, cons_text_widget, cons_str_widget, speed_var_cons, cons_event, consumed_string))
    start_cons_button.grid(row=6, column=1, padx=5, pady=5)

    stop_cons_button = tk.Button(frame, text="Stop Consumer", command=lambda: stop_consumer(cons_event))
    stop_cons_button.grid(row=7, column=1, padx=5, pady=5)

    exit_button = tk.Button(frame, text="Exit", command=root.quit)
    exit_button.grid(row=8, column=0, columnspan=2, pady=10)

    task_label = tk.Label(frame, text='''Задание: C  помощью мониторов Хоара организовать работу параллельных
                        вычислительных потоков. Первый поток записывает в файл случайные
                        символы. Второй поток считывает из файла символ и удаляет его, если это
                        не буква.''')
    task_label.grid(row=9, column=0, padx=5, pady=5)

    root.mainloop()

if __name__ == "__main__":
    main()

import tkinter as tk
from threading import Thread, Lock
import time
import random


class SmokerProblem:
    def __init__(self):
        self.smoking_index = [False, False, False]
        self.root = tk.Tk()
        self.root.title("Демонстрация проблемы курильщиков")

        self.ingredients = ["Табак", "Бумага", "Спички"]
        self.table_ingredients = []
        self.smokers = ["Курильщик с табаком", "Курильщик с бумагой", "Курильщик со спичками"]

        self.agent_lock = Lock()
        self.smoker_lock = [Lock(), Lock(), Lock()]

        for lock in self.smoker_lock:
            lock.acquire()

        self.status = tk.StringVar()
        self.status.set("Ожидание агента...")

        self.label = tk.Label(self.root, textvariable=self.status)
        self.label.pack(pady=20)

        self.start_button = tk.Button(self.root, text="Начать симуляцию", command=self.start_simulation)
        self.start_button.pack(pady=10)

        self.quit_button = tk.Button(self.root, text="Выход", command=self.root.quit)
        self.quit_button.pack(pady=10)

        self.agent_speed_label = tk.Label(self.root, text="Скорость агента (сек)")
        self.agent_speed_label.pack()
        self.agent_speed_slider = tk.Scale(self.root, from_=1, to=6, orient=tk.HORIZONTAL)
        self.agent_speed_slider.pack()

        self.indicators = []
        self.speed_sliders = []
        for i in range(3):
            frame = tk.Frame(self.root)
            frame.pack(pady=5)
            tk.Label(frame, text=self.smokers[i]).pack(side=tk.LEFT)
            indicator_frame = tk.Frame(frame)
            indicator_frame.pack(side=tk.LEFT)
            indicators = []
            for j in range(3):
                indicator = tk.Label(indicator_frame, text=self.ingredients[j], bg="red", width=10)
                indicator.pack(side=tk.LEFT, padx=2)
                indicators.append(indicator)
            smoking_indicator = tk.Label(indicator_frame, text="Курение", bg="red", width=10)
            smoking_indicator.pack(side=tk.LEFT, padx=2)
            indicators.append(smoking_indicator)
            self.indicators.append(indicators)

            speed_slider = tk.Scale(frame, from_=1, to=6, orient=tk.HORIZONTAL, label="Скорость (сек)")
            speed_slider.pack(side=tk.RIGHT)
            self.speed_sliders.append(speed_slider)

        self.initialize_smoker_indicators()

    def initialize_smoker_indicators(self):
        for i in range(3):
            self.indicators[i][i].config(bg="green")

    def start_simulation(self):
        self.start_button.config(state=tk.DISABLED)
        self.agent_thread = Thread(target=self.agent)
        self.agent_thread.start()
        self.smoker_threads = []
        for i in range(3):
            thread = Thread(target=self.smoker, args=(i,))
            thread.start()
            self.smoker_threads.append(thread)

    def agent(self):
        while True:
            self.agent_lock.acquire()
            # Агент выкладывает два случайных ингредиента на стол
            self.table_ingredients = random.sample(self.ingredients, 2)

            # Обновление индикаторов ингредиентов на столе
            self.update_indicators()

            self.status.set(f"Агент выложил {self.table_ingredients}")
            time.sleep(1)  # Время на выкладывание ингредиентов

            # Уведомление курильщиков
            for lock in self.smoker_lock:
                lock.release()

            time.sleep(self.agent_speed_slider.get())  # Время ожидания перед следующей выкладкой ингредиентов

    def smoker(self, index):
        while True:
            self.smoker_lock[index].acquire()

            if len(self.table_ingredients) == 2:
                missing_ingredient = list(set(self.ingredients) - set(self.table_ingredients))[0]

                if self.ingredients[index] == missing_ingredient:
                    self.status.set(f"{self.smokers[index]} курит")
                    self.table_ingredients.clear()
                    self.smoking_index[index] = True
                    # Обновление индикаторов курения
                    self.update_indicators()

                    time.sleep(self.speed_sliders[index].get())  # Время на курение

                    # Сброс индикатора курения и уведомление агента
                    self.smoking_index[index] = False
                    self.update_indicators()
                    self.agent_lock.release()
                else:
                    self.smoker_lock[index].release()

            self.update_indicators()

    def update_indicators(self):
        for i in range(3):
            if self.smoking_index[i]:
                self.indicators[i][3].config(bg="green")
            else:
                self.indicators[i][3].config(bg="red")
        for i in range(3):
            for j in range(3):
                if j != i:
                    if self.ingredients[j] in self.table_ingredients or self.smoking_index[i]:
                        self.indicators[i][j].config(bg="green")
                    else:
                        self.indicators[i][j].config(bg="red")

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = SmokerProblem()
    app.run()

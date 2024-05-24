import tkinter as tk
from threading import Thread, Lock
import time
import random


class SmokerProblem:
    def __init__(self):
        self.smoking_index = [False, False, False]
        self.want_to_smoke_index = [False, False, False]
        self.root = tk.Tk()
        self.root.title("Демонстрация проблемы курильщиков")

        self.ingredients = ["Табак", "Бумага", "Спички"]
        self.table_ingredients = []
        self.smokers = ["Курильщик с табаком", "Курильщик с бумагой", "Курильщик со спичками"]

        self.agent_lock = Lock()
        self.smoker_lock = [Lock(), Lock(), Lock()]
        self.exit_flag = False

        for lock in self.smoker_lock:
            lock.acquire()

        self.status = tk.StringVar()
        self.status.set("Ожидание агента...")

        self.label = tk.Label(self.root, textvariable=self.status)
        self.label.pack(pady=20)

        self.start_button = tk.Button(self.root, text="Начать симуляцию", command=self.start_simulation)
        self.start_button.pack(pady=10)

        self.quit_button = tk.Button(self.root, text="Выход", command=self.stop_simulation)
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

        self.task_label = tk.Label(self.root, text='''Задание: Задачу о курильщиках решить с помощью алгоритма Питерсона.''')
        self.task_label.pack()

        self.initialize_smoker_indicators()

    def initialize_smoker_indicators(self):
        for i in range(3):
            self.indicators[i][i].config(bg="green")

    def start_simulation(self):
        self.start_button.config(state=tk.DISABLED)
        self.agent_thread = Thread(target=self.agent, daemon=True)
        self.agent_thread.start()
        self.smoker_threads = []
        for i in range(3):
            thread = Thread(target=self.smoker, args=(i,), daemon=True)
            thread.start()
            self.smoker_threads.append(thread)

    def stop_simulation(self):
        self.exit_flag = True
        self.root.after(100, self.root.quit)  # Закрытие root через 100 миллисекунд

    def agent(self):
        while not self.exit_flag:
            self.agent_lock.acquire()
            if self.exit_flag:
                break
            # Агент выкладывает два случайных ингредиента на стол
            self.table_ingredients = random.sample(self.ingredients, 2)

            # Обновление индикаторов ингредиентов на столе
            self.update_indicators()

            self.status.set(f"Агент выложил {self.table_ingredients}")
            time.sleep(1)  # Время на выкладывание ингредиентов

            # Уведомление курильщиков
            for lock in self.smoker_lock:
                if lock.locked():
                    lock.release()

            time.sleep(self.agent_speed_slider.get())  # Время ожидания перед следующей выкладкой ингредиентов

    def smoker(self, index):
        while not self.exit_flag:
            self.smoker_lock[index].acquire()
            if self.exit_flag:
                break
            if not self.want_to_smoke_index[index]:
                time.sleep(self.speed_sliders[index].get())  # Время ожидания перед тем как захочет курить
                self.want_to_smoke_index[index] = True
                self.update_indicators()

            if len(self.table_ingredients) == 2 and self.want_to_smoke_index[index]:
                missing_ingredient = list(set(self.ingredients) - set(self.table_ingredients))[0]

                if self.ingredients[index] == missing_ingredient:
                    self.status.set(f"{self.smokers[index]} курит")
                    self.table_ingredients.clear()
                    self.smoking_index[index] = True
                    # Обновление индикаторов курения
                    self.update_indicators()

                    time.sleep(1)  # Время на курение

                    # Сброс индикатора курения и уведомление агента
                    self.smoking_index[index] = False
                    self.update_indicators()
                    self.agent_lock.release()
                    self.want_to_smoke_index[index] = False
            else:
                self.smoker_lock[index].release()
            self.update_indicators()

    def update_indicators(self):
        for i in range(3):
            if self.smoking_index[i]:
                self.indicators[i][3].config(bg="green")
            elif self.want_to_smoke_index[i]:
                self.indicators[i][3].config(bg="yellow")
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
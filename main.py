import tkinter as tk
from tkinter import ttk, messagebox
import requests
import json
import os
import datetime

# --- НАСТРОЙКИ ---
API_KEY = "openexchangerates.org"
API_URL = f"https://v6.exchangerate-api.com/v6/{API_KEY}/latest/"
HISTORY_FILE = "history.json"


# ------------------

class CurrencyConverter:
    def __init__(self, root):
        self.root = root
        self.root.title("Currency Converter")
        self.root.geometry("600x450")

        # Список валют (можно расширить)
        self.currencies = ["USD", "EUR", "RUB", "GBP", "JPY", "CNY"]

        self.create_widgets()
        self.load_history()

    def create_widgets(self):
        # Выбор валют
        tk.Label(self.root, text="Из:").grid(row=0, column=0, padx=10, pady=10, sticky="e")
        self.from_currency = ttk.Combobox(self.root, values=self.currencies)
        self.from_currency.current(0)
        self.from_currency.grid(row=0, column=1, padx=10, pady=10)

        tk.Label(self.root, text="В:").grid(row=1, column=0, padx=10, pady=10, sticky="e")
        self.to_currency = ttk.Combobox(self.root, values=self.currencies)
        self.to_currency.current(1)
        self.to_currency.grid(row=1, column=1, padx=10, pady=10)

        # Ввод суммы
        tk.Label(self.root, text="Сумма:").grid(row=2, column=0, padx=10, pady=10, sticky="e")
        self.amount_entry = tk.Entry(self.root)
        self.amount_entry.grid(row=2, column=1, padx=10, pady=10)

        # Кнопка конвертации
        self.convert_btn = tk.Button(self.root, text="Конвертировать", command=self.convert)
        self.convert_btn.grid(row=3, column=0, columnspan=2, pady=20)

        # Результат
        self.result_label = tk.Label(self.root, text="", font=("Arial", 12))
        self.result_label.grid(row=4, column=0, columnspan=2)

        # Таблица истории
        self.history_tree = ttk.Treeview(self.root, columns=("from", "to", "amount", "result"), show="headings")

        self.history_tree.heading("from", text="Из")
        self.history_tree.heading("to", text="В")
        self.history_tree.heading("amount", text="Сумма")
        self.history_tree.heading("result", text="Результат")

        self.history_tree.grid(row=5, column=0, columnspan=2, padx=10, pady=(0, 10), sticky="nsew")

        # Настройка веса сетки для растягивания таблицы
        self.root.grid_rowconfigure(5, weight=1)
        self.root.grid_columnconfigure(1, weight=1)

    def is_valid_amount(self):
        value = self.amount_entry.get()
        try:
            amount = float(value)
            if amount <= 0:
                messagebox.showerror("Ошибка", "Сумма должна быть больше нуля!")
                return False
            return True
        except ValueError:
            messagebox.showerror("Ошибка", "Введите корректное число!")
            return False

    def get_rate(self):
        base = self.from_currency.get()
        target = self.to_currency.get()

        try:
            response = requests.get(f"{API_URL}{base}")
            data = response.json()

            if data.get('result') != 'success':
                raise Exception(data.get('error-type', 'Неизвестная ошибка API'))

            rate = data['conversion_rates'].get(target)
            if rate is None:
                raise Exception(f"Курс для {target} не найден.")
            return rate

        except Exception as e:
            messagebox.showerror("Ошибка API", str(e))
            return None

    def convert(self):
        if not self.is_valid_amount():
            return

        rate = self.get_rate()
        if rate is None:
            return

        amount = float(self.amount_entry.get())
        result = round(amount * rate, 2)

        self.result_label.config(text=f"Результат: {result} {self.to_currency.get()}")

        # Добавление в историю
        history_entry = {
            "from": self.from_currency.get(),
            "to": self.to_currency.get(),
            "amount": amount,
            "result": result,
            "rate": rate,
            "timestamp": str(datetime.datetime.now())
        }

        self.history.append(history_entry)

        # Обновление таблицы и сохранение
        self.update_history_tree()
        self.save_history()

    def load_history(self):
        if os.path.exists(HISTORY_FILE):
            with open(HISTORY_FILE, 'r') as f:
                try:
                    self.history = json.load(f)
                except json.JSONDecodeError:
                    self.history = []
                    self.save_history()  # Пересоздаём файл если он битый
                    print("Файл истории повреждён. Создан новый.")
                    messagebox.showwarning("История", "Файл истории повреждён. История очищена.")
                    return
                else:
                    print("История успешно загружена.")
                    messagebox.showinfo("История", "История успешно загружена.")
                    self.update_history_tree()
                    return

        # Если файла нет
        self.history = []

    def save_history(self):
        with open(HISTORY_FILE, 'w') as f:
            json.dump(self.history, f, indent=4)

    def update_history_tree(self):
        for i in self.history_tree.get_children():
            self.history_tree.delete(i)

        for entry in reversed(self.history):  # Показываем последние сверху
            self.history_tree.insert("", tk.END, values=(
                entry["from"],
                entry["to"],
                entry["amount"],
                entry["result"]
            ))


if __name__ == "__main__":
    root = tk.Tk()
    app = CurrencyConverter(root)
    root.mainloop()
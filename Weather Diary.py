import json
import os
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox

class WeatherDiary:
    def __init__(self, root):
        self.root = root
        self.root.title("Weather Diary - Дневник погоды")
        self.root.geometry("750x550")
        self.root.resizable(True, True)

        self.data_file = "weather_data.json"
        self.entries = []
        self.load_from_file()

        self.create_widgets()
        self.refresh_table()

    def create_widgets(self):
        # Рамка ввода
        input_frame = tk.LabelFrame(self.root, text="Добавить запись", padx=10, pady=10)
        input_frame.pack(fill="x", padx=10, pady=5)

        tk.Label(input_frame, text="Дата (ГГГГ-ММ-ДД):").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        self.date_entry = tk.Entry(input_frame, width=12)
        self.date_entry.grid(row=0, column=1, padx=5, pady=5)
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))

        tk.Label(input_frame, text="Температура (°C):").grid(row=0, column=2, sticky="e", padx=5, pady=5)
        self.temp_entry = tk.Entry(input_frame, width=8)
        self.temp_entry.grid(row=0, column=3, padx=5, pady=5)

        tk.Label(input_frame, text="Описание:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        self.desc_entry = tk.Entry(input_frame, width=40)
        self.desc_entry.grid(row=1, column=1, columnspan=3, padx=5, pady=5)

        self.precip_var = tk.BooleanVar()
        tk.Checkbutton(input_frame, text="Осадки", variable=self.precip_var).grid(row=2, column=1, sticky="w", padx=5, pady=5)

        # Рамка фильтрации
        filter_frame = tk.LabelFrame(self.root, text="Фильтрация", padx=10, pady=10)
        filter_frame.pack(fill="x", padx=10, pady=5)

        tk.Label(filter_frame, text="Дата (ГГГГ-ММ-ДД):").grid(row=0, column=0, padx=5, pady=5)
        self.filter_date_entry = tk.Entry(filter_frame, width=12)
        self.filter_date_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(filter_frame, text="Температура выше (°C):").grid(row=1, column=0, padx=5, pady=5)
        self.filter_temp_entry = tk.Entry(filter_frame, width=8)
        self.filter_temp_entry.grid(row=1, column=1, padx=5, pady=5)

        btn_frame = tk.Frame(filter_frame)
        btn_frame.grid(row=2, column=0, columnspan=2, pady=5)
        tk.Button(btn_frame, text="Применить фильтр", command=self.apply_filter).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Сбросить фильтр", command=self.reset_filter).pack(side="left", padx=5)

        # Таблица
        self.tree_frame = tk.Frame(self.root)
        self.tree_frame.pack(fill="both", expand=True, padx=10, pady=5)

        columns = ("Дата", "Температура (°C)", "Описание", "Осадки")
        self.tree = ttk.Treeview(self.tree_frame, columns=columns, show="headings")
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150)

        scrollbar = ttk.Scrollbar(self.tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Кнопки управления
        control_frame = tk.Frame(self.root)
        control_frame.pack(fill="x", padx=10, pady=10)

        tk.Button(control_frame, text="➕ Добавить запись", command=self.add_entry, bg="#4CAF50", fg="white").pack(side="left", padx=5)
        tk.Button(control_frame, text="🗑 Удалить выбранную", command=self.delete_entry, bg="#f44336", fg="white").pack(side="left", padx=5)
        tk.Button(control_frame, text="💾 Сохранить в JSON", command=self.save_to_file, bg="#2196F3", fg="white").pack(side="left", padx=5)

    def validate_date(self, date_str):
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
            return True
        except ValueError:
            return False

    def add_entry(self):
        date = self.date_entry.get().strip()
        temp = self.temp_entry.get().strip()
        desc = self.desc_entry.get().strip()
        precip = "Да" if self.precip_var.get() else "Нет"

        if not self.validate_date(date):
            messagebox.showerror("Ошибка", "Неверный формат даты. Используйте ГГГГ-ММ-ДД")
            return
        try:
            temp_val = float(temp)
        except ValueError:
            messagebox.showerror("Ошибка", "Температура должна быть числом")
            return
        if not desc:
            messagebox.showerror("Ошибка", "Описание не может быть пустым")
            return

        self.entries.append({
            "date": date,
            "temperature": temp_val,
            "description": desc,
            "precipitation": precip
        })

        self.temp_entry.delete(0, tk.END)
        self.desc_entry.delete(0, tk.END)
        self.precip_var.set(False)

        self.save_to_file()
        self.refresh_table()
        messagebox.showinfo("Успех", "Запись добавлена")

    def delete_entry(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите запись для удаления")
            return
        if messagebox.askyesno("Подтверждение", "Удалить выбранную запись?"):
            for item in selected:
                values = self.tree.item(item, "values")
                self.entries = [e for e in self.entries if not (
                    e["date"] == values[0] and
                    str(e["temperature"]) == values[1] and
                    e["description"] == values[2] and
                    e["precipitation"] == values[3]
                )]
            self.save_to_file()
            self.refresh_table()
            messagebox.showinfo("Успех", "Запись удалена")

    def apply_filter(self):
        filter_date = self.filter_date_entry.get().strip()
        filter_temp = self.filter_temp_entry.get().strip()

        filtered = self.entries.copy()
        if filter_date:
            if not self.validate_date(filter_date):
                messagebox.showerror("Ошибка", "Неверный формат даты фильтра")
                return
            filtered = [e for e in filtered if e["date"] == filter_date]
        if filter_temp:
            try:
                threshold = float(filter_temp)
                filtered = [e for e in filtered if e["temperature"] > threshold]
            except ValueError:
                messagebox.showerror("Ошибка", "Температура фильтра должна быть числом")
                return
        self.display_entries(filtered)

    def reset_filter(self):
        self.filter_date_entry.delete(0, tk.END)
        self.filter_temp_entry.delete(0, tk.END)
        self.refresh_table()

    def display_entries(self, entries_list):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for e in entries_list:
            self.tree.insert("", "end", values=(e["date"], e["temperature"], e["description"], e["precipitation"]))

    def refresh_table(self):
        if self.filter_date_entry.get() or self.filter_temp_entry.get():
            self.apply_filter()
        else:
            self.display_entries(self.entries)

    def save_to_file(self):
        try:
            with open(self.data_file, "w", encoding="utf-8") as f:
                json.dump(self.entries, f, indent=4, ensure_ascii=False)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить: {e}")

    def load_from_file(self):
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, "r", encoding="utf-8") as f:
                    self.entries = json.load(f)
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось загрузить: {e}")
                self.entries = []

if __name__ == "__main__":
    root = tk.Tk()
    app = WeatherDiary(root)
    root.mainloop()
import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
import numpy as np
import re
from datetime import datetime


# Создание базы данных и таблицы
def create_db():
    conn = sqlite3.connect('.venv/accounting.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            education TEXT NOT NULL,
            position TEXT NOT NULL,
            hire_date TEXT NOT NULL,
            salary REAL NOT NULL
        )
    ''')

    # Добавляем больше тестовых данных
    test_data = [
        ('Иванов И.И.', 'Высшее', 'Менеджер', '15.05.2018', 42000.0),
        ('Петров П.П.', 'Среднее', 'Инженер', '10.10.2019', 45000.0),
        ('Сидоров С.С.', 'Высшее', 'Аналитик', '20.03.2020', 60000.0),
        ('Кузнецова А.А.', 'Среднее', 'Техник', '05.12.2021', 38000.0),
        ('Смирнов Д.Д.', 'Высшее', 'Разработчик', '15.08.2022', 75000.0),
        ('Васильева Е.Е.', 'Среднее', 'Тестировщик', '25.02.2023', 40000.0)
    ]

    cursor.executemany('''
        INSERT INTO employees (name, education, position, hire_date, salary)
        VALUES (?, ?, ?, ?, ?)
    ''', test_data)

    conn.commit()
    conn.close()


class AccountingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Бухгалтерия")
        self.current_edit_id = None  # Для хранения ID редактируемой записи

        # Поля ввода
        self.name_var = tk.StringVar()
        self.education_var = tk.StringVar()
        self.position_var = tk.StringVar()
        self.hire_date_var = tk.StringVar()
        self.salary_var = tk.DoubleVar()

        # Визуальные элементы
        self.create_widgets()

    def create_widgets(self):
        # Поля ввода
        tk.Label(self.root, text="ФИО:").grid(row=0, column=0)
        tk.Entry(self.root, textvariable=self.name_var).grid(row=0, column=1)

        tk.Label(self.root, text="Образование:").grid(row=1, column=0)
        tk.Entry(self.root, textvariable=self.education_var).grid(row=1, column=1)

        tk.Label(self.root, text="Должность:").grid(row=2, column=0)
        tk.Entry(self.root, textvariable=self.position_var).grid(row=2, column=1)

        tk.Label(self.root, text="Дата поступления (ДД.ММ.ГГГГ):").grid(row=3, column=0)
        date_entry = tk.Entry(self.root, textvariable=self.hire_date_var, validate="key",
                              validatecommand=(self.root.register(self.validate_date), '%P'))
        date_entry.grid(row=3, column=1)

        tk.Label(self.root, text="Оклад:").grid(row=4, column=0)
        tk.Entry(self.root, textvariable=self.salary_var).grid(row=4, column=1)

        # Кнопки управления
        tk.Button(self.root, text="Добавить/Сохранить", command=self.save_employee).grid(row=5, column=0)
        tk.Button(self.root, text="Очистить", command=self.clear_fields).grid(row=5, column=1)
        tk.Button(self.root, text="Просмотр записей", command=self.view_records).grid(row=6, column=0)
        tk.Button(self.root, text="Анализ данных", command=self.analyze_data).grid(row=6, column=1)
        tk.Button(self.root, text="Прогноз зарплат", command=self.forecast_salary_growth).grid(row=7, column=0)

    def save_employee(self):
        if self.current_edit_id:
            # Режим редактирования
            self.update_employee()
        else:
            # Режим добавления
            self.add_employee()

    def validate_date(self, text):
        if len(text) > 10:
            return False
        if re.match(r"^\d{0,2}[.]?\d{0,2}[.]?\d{0,4}$", text):
            return True
        return False

    def add_employee(self):
        conn = sqlite3.connect('.venv/accounting.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO employees (name, education, position, hire_date, salary)
            VALUES (?, ?, ?, ?, ?)
        ''', (self.name_var.get(), self.education_var.get(), self.position_var.get(),
              self.hire_date_var.get(), self.salary_var.get()))
        conn.commit()
        conn.close()
        messagebox.showinfo("Успех", "Сотрудник добавлен!")
        self.clear_fields()

    def update_employee(self):
        conn = sqlite3.connect('.venv/accounting.db')
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE employees SET
                name = ?,
                education = ?,
                position = ?,
                hire_date = ?,
                salary = ?
            WHERE id = ?
        ''', (self.name_var.get(), self.education_var.get(), self.position_var.get(),
              self.hire_date_var.get(), self.salary_var.get(), self.current_edit_id))
        conn.commit()
        conn.close()
        messagebox.showinfo("Успех", "Данные обновлены!")
        self.clear_fields()
        self.current_edit_id = None

    def clear_fields(self):
        self.name_var.set("")
        self.education_var.set("")
        self.position_var.set("")
        self.hire_date_var.set("")
        self.salary_var.set(0.0)
        self.current_edit_id = None

    def view_records(self):
        view_window = tk.Toplevel(self.root)
        view_window.title("Просмотр записей")

        # Treeview для отображения данных
        tree = ttk.Treeview(view_window, columns=('ID', 'Name', 'Education', 'Position', 'Hire Date', 'Salary'),
                            show='headings')
        tree.heading('ID', text='ID')
        tree.heading('Name', text='ФИО')
        tree.heading('Education', text='Образование')
        tree.heading('Position', text='Должность')
        tree.heading('Hire Date', text='Дата приема')
        tree.heading('Salary', text='Оклад')

        # Кнопки управления
        tk.Button(view_window, text="Обновить", command=lambda: self.load_data(tree)).pack()
        tk.Button(view_window, text="Удалить", command=lambda: self.delete_record(tree)).pack()
        tk.Button(view_window, text="Редактировать", command=lambda: self.edit_record(tree)).pack()

        tree.pack(expand=True, fill='both')
        self.load_data(tree)

    def load_data(self, tree):
        # Очистка предыдущих данных
        for item in tree.get_children():
            tree.delete(item)

        conn = sqlite3.connect('.venv/accounting.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM employees")
        rows = cursor.fetchall()
        conn.close()

        for row in rows:
            tree.insert('', 'end', values=row)

    def delete_record(self, tree):
        selected_item = tree.selection()
        if not selected_item:
            messagebox.showerror("Ошибка", "Выберите запись для удаления")
            return

        if messagebox.askyesno("Подтверждение", "Удалить выбранную запись?"):
            record_id = tree.item(selected_item[0], 'values')[0]

            conn = sqlite3.connect('.venv/accounting.db')
            cursor = conn.cursor()
            cursor.execute("DELETE FROM employees WHERE id = ?", (record_id,))
            conn.commit()
            conn.close()

            self.load_data(tree)

    def edit_record(self, tree):
        selected_item = tree.selection()
        if not selected_item:
            messagebox.showerror("Ошибка", "Выберите запись для редактирования")
            return

        record_data = tree.item(selected_item[0], 'values')
        self.current_edit_id = record_data[0]

        # Заполнение полей ввода
        self.name_var.set(record_data[1])
        self.education_var.set(record_data[2])
        self.position_var.set(record_data[3])
        self.hire_date_var.set(record_data[4])
        self.salary_var.set(record_data[5])

    def analyze_data(self):
        conn = sqlite3.connect('.venv/accounting.db')
        df = pd.read_sql_query("SELECT education, AVG(salary) as avg_salary FROM employees GROUP BY education", conn)
        conn.close()

        df.plot(kind='bar', x='education', y='avg_salary', title='Средняя зарплата по образованию')
        plt.ylabel('Средняя зарплата')
        plt.show()

    def forecast_salary_growth(self):
        try:
            conn = sqlite3.connect('.venv/accounting.db')
            df = pd.read_sql_query("SELECT hire_date, salary FROM employees", conn)

            if df.empty:
                messagebox.showwarning("Ошибка", "Нет данных для прогнозирования")
                return

            # Преобразование дат с явным указанием формата
            df['hire_date'] = pd.to_datetime(df['hire_date'], format='%d.%m.%Y', errors='coerce')

            # Удаление некорректных записей
            df = df.dropna(subset=['hire_date'])

            if df.empty:
                messagebox.showwarning("Ошибка", "Нет корректных данных для прогнозирования")
                return

            # Расчет стажа в годах с точностью до месяца
            current_date = datetime.now()
            df['experience'] = df['hire_date'].apply(
                lambda x: (current_date - x).days / 365.25
            )

            # Фильтрация данных
            df = df[df['experience'] > 0]  # Только сотрудники с положительным стажем

            if len(df) < 3:
                messagebox.showwarning("Ошибка", "Недостаточно данных для построения прогноза")
                return

            # Подготовка данных для модели
            X = df[['experience']]
            y = df['salary']

            # Обучение модели с весами (более новые данные имеют больший вес)
            model = LinearRegression()
            model.fit(X, y)

            # Прогноз на следующие 3 года
            max_experience = df['experience'].max()
            future_years = np.arange(max_experience + 1, max_experience + 4).reshape(-1, 1)

            # Создаем DataFrame для предсказания
            future_df = pd.DataFrame(future_years, columns=['experience'])
            predictions = model.predict(future_df)

            # Форматируем результат
            result = [
                "Прогноз роста окладов:",
                *[f"Через {i + 1} год: {pred:.2f} руб." for i, pred in enumerate(predictions)]
            ]

            messagebox.showinfo("Прогноз зарплат", "\n".join(result))

        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка прогнозирования: {str(e)}")
        finally:
            conn.close()


if __name__ == "__main__":
    create_db()
    root = tk.Tk()
    app = AccountingApp(root)
    root.mainloop()
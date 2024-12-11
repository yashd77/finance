import tkinter as tk
from tkinter import ttk, messagebox
from expense_tracker import ExpenseTracker
from budget_manager import BudgetManager
from data_visualizer import DataVisualizer
import mysql.connector
from mysql.connector import Error

class PersonalFinanceManager(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Personal Finance Manager")
        self.geometry("800x600")

        self.db_config = {
            'host': 'localhost',
            'user': 'root',
            'password': '0000',
            'database': 'personal_finance'
        }

        if self.create_database():
            self.budget_manager = BudgetManager(self.db_config)
            self.expense_tracker = ExpenseTracker(self.db_config)
            self.data_visualizer = DataVisualizer(self.expense_tracker, self.budget_manager)
            self.create_widgets()
        else:
            self.show_error_and_exit()

    def create_database(self):
        try:
            conn = mysql.connector.connect(
                host=self.db_config['host'],
                user=self.db_config['user'],
                password=self.db_config['password']
            )
            if conn.is_connected():
                cursor = conn.cursor()
                cursor.execute(f"CREATE DATABASE IF NOT EXISTS {self.db_config['database']}")
                cursor.close()
                conn.close()
                return True
        except Error as e:
            messagebox.showerror("Database Error", f"Error creating database: {e}")
            return False

    def create_widgets(self):
        notebook = ttk.Notebook(self)
        notebook.pack(expand=True, fill="both")

        budget_frame = ttk.Frame(notebook)
        expense_frame = ttk.Frame(notebook)
        visualize_frame = ttk.Frame(notebook)

        notebook.add(budget_frame, text="Budget Manager")
        notebook.add(expense_frame, text="Expense Tracker")
        notebook.add(visualize_frame, text="Visualize Data")

        self.budget_manager.create_widgets(budget_frame)
        self.expense_tracker.create_widgets(expense_frame)
        self.data_visualizer.create_widgets(visualize_frame)

    def show_error_and_exit(self):
        messagebox.showerror("Fatal Error", "Unable to connect to the database. The application will now exit.")
        self.destroy()

if __name__ == "__main__":
    app = PersonalFinanceManager()
    app.mainloop()
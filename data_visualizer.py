import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from collections import defaultdict
from decimal import Decimal

class DataVisualizer:
    def __init__(self, expense_tracker, budget_manager):
        self.expense_tracker = expense_tracker
        self.budget_manager = budget_manager

    def create_widgets(self, parent):
        self.parent = parent

        ttk.Button(parent, text="Visualize Expenses", command=self.visualize_expenses).pack(pady=10)
        ttk.Button(parent, text="Compare to Budget", command=self.compare_to_budget).pack(pady=10)

        self.canvas_frame = ttk.Frame(parent)
        self.canvas_frame.pack(expand=True, fill="both")

    def visualize_expenses(self):
        expenses = self.expense_tracker.get_expenses()
        categories = defaultdict(float)

        for date, category, amount in expenses:
            categories[category] += float(amount)

        fig, ax = plt.subplots(figsize=(8, 6))
        ax.pie(categories.values(), labels=categories.keys(), autopct='%1.1f%%')
        ax.set_title("Expense Distribution by Category")

        self.display_chart(fig)

    def compare_to_budget(self):
        expenses = self.expense_tracker.get_expenses()
        budgets = dict(self.budget_manager.get_budgets())

        categories = defaultdict(float)
        for date, category, amount in expenses:
            categories[category] += float(amount)

        fig, ax = plt.subplots(figsize=(10, 6))
        x = list(budgets.keys())
        budget_amounts = [budgets[cat] for cat in x]
        expense_amounts = [categories[cat] for cat in x]

        ax.bar(x, budget_amounts, label="Budget")
        ax.bar(x, expense_amounts, label="Actual Expenses")
        ax.set_ylabel("Amount")
        ax.set_title("Budget vs Actual Expenses by Category")
        ax.legend()

        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()

        self.display_chart(fig)

    def display_chart(self, figure):
        for widget in self.canvas_frame.winfo_children():
            widget.destroy()

        canvas = FigureCanvasTkAgg(figure, master=self.canvas_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(expand=True, fill="both")
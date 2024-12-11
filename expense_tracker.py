import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
from mysql.connector import Error
from datetime import datetime

class ExpenseTracker:
    def __init__(self, db_config):
        self.db_config = db_config
        self.create_table()

    def create_table(self):
        try:
            conn = mysql.connector.connect(**self.db_config)
            if conn.is_connected():
                cursor = conn.cursor()
                cursor.execute('''
                CREATE TABLE IF NOT EXISTS expenses (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    date DATE,
                    category VARCHAR(255),
                    amount DECIMAL(10, 2)
                )
                ''')
                conn.commit()
        except Error as e:
            messagebox.showerror("Database Error", f"Error creating expenses table: {e}")
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()

    def create_widgets(self, parent):
        self.parent = parent

        # Expense input fields
        ttk.Label(parent, text="Date:").grid(row=0, column=0, padx=5, pady=5)
        self.date_entry = ttk.Entry(parent)
        self.date_entry.grid(row=0, column=1, padx=5, pady=5)
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))

        ttk.Label(parent, text="Category:").grid(row=1, column=0, padx=5, pady=5)
        self.category_entry = ttk.Entry(parent)
        self.category_entry.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(parent, text="Amount:").grid(row=2, column=0, padx=5, pady=5)
        self.amount_entry = ttk.Entry(parent)
        self.amount_entry.grid(row=2, column=1, padx=5, pady=5)

        ttk.Button(parent, text="Add Expense", command=self.add_expense).grid(row=3, column=0, pady=10)
        ttk.Button(parent, text="Update Expense", command=self.update_expense).grid(row=3, column=1, pady=10)

        # Expense list
        self.tree = ttk.Treeview(parent, columns=("ID", "Date", "Category", "Amount"), show="headings")
        self.tree.heading("ID", text="ID")
        self.tree.heading("Date", text="Date")
        self.tree.heading("Category", text="Category")
        self.tree.heading("Amount", text="Amount")
        self.tree.grid(row=4, column=0, columnspan=2, padx=5, pady=5)

        # Bind the treeview selection to populate the entry fields
        self.tree.bind("<<TreeviewSelect>>", self.item_selected)

        # Delete button
        ttk.Button(parent, text="Delete Expense", command=self.delete_expense).grid(row=5, column=0, columnspan=2, pady=10)

        self.load_expenses()

    def add_expense(self):
        date = self.date_entry.get()
        category = self.category_entry.get()
        amount = self.amount_entry.get()

        if not date or not category or not amount:
            messagebox.showerror("Error", "Please fill in all fields")
            return

        try:
            amount = float(amount)
        except ValueError:
            messagebox.showerror("Error", "Amount must be a number")
            return

        try:
            conn = mysql.connector.connect(**self.db_config)
            if conn.is_connected():
                cursor = conn.cursor()
                cursor.execute("INSERT INTO expenses (date, category, amount) VALUES (%s, %s, %s)",
                               (date, category, amount))
                conn.commit()
                messagebox.showinfo("Success", "Expense added successfully")
        except Error as e:
            messagebox.showerror("Database Error", f"Error adding expense: {e}")
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()

        self.load_expenses()
        self.clear_entries()

    def update_expense(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "Please select an expense to update")
            return

        expense_id = self.tree.item(selected_item)['values'][0]
        date = self.date_entry.get()
        category = self.category_entry.get()
        amount = self.amount_entry.get()

        if not date or not category or not amount:
            messagebox.showerror("Error", "Please fill in all fields")
            return

        try:
            amount = float(amount)
        except ValueError:
            messagebox.showerror("Error", "Amount must be a number")
            return

        try:
            conn = mysql.connector.connect(**self.db_config)
            if conn.is_connected():
                cursor = conn.cursor()
                cursor.execute("UPDATE expenses SET date=%s, category=%s, amount=%s WHERE id=%s",
                               (date, category, amount, expense_id))
                conn.commit()
                messagebox.showinfo("Success", "Expense updated successfully")
        except Error as e:
            messagebox.showerror("Database Error", f"Error updating expense: {e}")
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()

        self.load_expenses()
        self.clear_entries()

    def delete_expense(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "Please select an expense to delete")
            return

        expense_id = self.tree.item(selected_item)['values'][0]

        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this expense?"):
            try:
                conn = mysql.connector.connect(**self.db_config)
                if conn.is_connected():
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM expenses WHERE id=%s", (expense_id,))
                    conn.commit()
                    messagebox.showinfo("Success", "Expense deleted successfully")
            except Error as e:
                messagebox.showerror("Database Error", f"Error deleting expense: {e}")
            finally:
                if conn.is_connected():
                    cursor.close()
                    conn.close()

            self.load_expenses()
            self.clear_entries()

    def load_expenses(self):
        self.tree.delete(*self.tree.get_children())
        try:
            conn = mysql.connector.connect(**self.db_config)
            if conn.is_connected():
                cursor = conn.cursor()
                cursor.execute("SELECT id, date, category, amount FROM expenses ORDER BY date DESC")
                for row in cursor.fetchall():
                    self.tree.insert("", "end", values=row)
        except Error as e:
            messagebox.showerror("Database Error", f"Error loading expenses: {e}")
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()

    def clear_entries(self):
        self.date_entry.delete(0, tk.END)
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.category_entry.delete(0, tk.END)
        self.amount_entry.delete(0, tk.END)

    def item_selected(self, event):
        selected_item = self.tree.selection()
        if selected_item:
            values = self.tree.item(selected_item)['values']
            self.date_entry.delete(0, tk.END)
            self.date_entry.insert(0, values[1])
            self.category_entry.delete(0, tk.END)
            self.category_entry.insert(0, values[2])
            self.amount_entry.delete(0, tk.END)
            self.amount_entry.insert(0, values[3])

    def get_expenses(self):
        try:
            conn = mysql.connector.connect(**self.db_config)
            if conn.is_connected():
                cursor = conn.cursor()
                cursor.execute("SELECT date, category, amount FROM expenses ORDER BY date")
                return cursor.fetchall()
        except Error as e:
            messagebox.showerror("Database Error", f"Error getting expenses: {e}")
            return []
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()
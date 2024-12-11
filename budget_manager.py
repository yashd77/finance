import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
from mysql.connector import Error

class BudgetManager:
    def __init__(self, db_config):
        self.db_config = db_config
        self.create_table()

    def create_table(self):
        try:
            conn = mysql.connector.connect(**self.db_config)
            if conn.is_connected():
                cursor = conn.cursor()
                cursor.execute('''
                CREATE TABLE IF NOT EXISTS budgets (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    category VARCHAR(255) UNIQUE,
                    amount DECIMAL(10, 2)
                )
                ''')
                conn.commit()
        except Error as e:
            messagebox.showerror("Database Error", f"Error creating budgets table: {e}")
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()

    def create_widgets(self, parent):
        self.parent = parent

        ttk.Label(parent, text="Category:").grid(row=0, column=0, padx=5, pady=5)
        self.category_entry = ttk.Entry(parent)
        self.category_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(parent, text="Budget Amount:").grid(row=1, column=0, padx=5, pady=5)
        self.amount_entry = ttk.Entry(parent)
        self.amount_entry.grid(row=1, column=1, padx=5, pady=5)

        ttk.Button(parent, text="Set Budget", command=self.set_budget).grid(row=2, column=0, pady=10)
        ttk.Button(parent, text="Update Budget", command=self.update_budget).grid(row=2, column=1, pady=10)

        self.tree = ttk.Treeview(parent, columns=("ID", "Category", "Budget Amount"), show="headings")
        self.tree.heading("ID", text="ID")
        self.tree.heading("Category", text="Category")
        self.tree.heading("Budget Amount", text="Budget Amount")
        self.tree.grid(row=3, column=0, columnspan=2, padx=5, pady=5)

        self.tree.bind("<<TreeviewSelect>>", self.item_selected)

        ttk.Button(parent, text="Delete Budget", command=self.delete_budget).grid(row=4, column=0, columnspan=2, pady=10)

        self.load_budgets()

    def set_budget(self):
        category = self.category_entry.get()
        amount = self.amount_entry.get()

        if not category or not amount:
            messagebox.showerror("Error", "Please fill in all fields")
            return

        try:
            amount = float(amount)
        except ValueError:
            messagebox.showerror("Error", "Budget amount must be a number")
            return

        try:
            conn = mysql.connector.connect(**self.db_config)
            if conn.is_connected():
                cursor = conn.cursor()
                cursor.execute("INSERT INTO budgets (category, amount) VALUES (%s, %s)",
                               (category, amount))
                conn.commit()
                messagebox.showinfo("Success", "Budget set successfully")
        except Error as e:
            if e.errno == 1062:
                messagebox.showerror("Error", "Category already exists. Use 'Update Budget' to modify.")
            else:
                messagebox.showerror("Database Error", f"Error setting budget: {e}")
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()

        self.load_budgets()
        self.clear_entries()

    def update_budget(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "Please select a budget to update")
            return

        budget_id = self.tree.item(selected_item)['values'][0]
        category = self.category_entry.get()
        amount = self.amount_entry.get()

        if not category or not amount:
            messagebox.showerror("Error", "Please fill in all fields")
            return

        try:
            amount = float(amount)
        except ValueError:
            messagebox.showerror("Error", "Budget amount must be a number")
            return

        try:
            conn = mysql.connector.connect(**self.db_config)
            if conn.is_connected():
                cursor = conn.cursor()
                cursor.execute("UPDATE budgets SET category=%s, amount=%s WHERE id=%s",
                               (category, amount, budget_id))
                conn.commit()
                messagebox.showinfo("Success", "Budget updated successfully")
        except Error as e:
            messagebox.showerror("Database Error", f"Error updating budget: {e}")
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()

        self.load_budgets()
        self.clear_entries()

    def delete_budget(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "Please select a budget to delete")
            return

        budget_id = self.tree.item(selected_item)['values'][0]

        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this budget?"):
            try:
                conn = mysql.connector.connect(**self.db_config)
                if conn.is_connected():
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM budgets WHERE id=%s", (budget_id,))
                    conn.commit()
                    messagebox.showinfo("Success", "Budget deleted successfully")
            except Error as e:
                messagebox.showerror("Database Error", f"Error deleting budget: {e}")
            finally:
                if conn.is_connected():
                    cursor.close()
                    conn.close()

            self.load_budgets()
            self.clear_entries()

    def load_budgets(self):
        self.tree.delete(*self.tree.get_children())
        try:
            conn = mysql.connector.connect(**self.db_config)
            if conn.is_connected():
                cursor = conn.cursor()
                cursor.execute("SELECT id, category, amount FROM budgets ORDER BY category")
                for row in cursor.fetchall():
                    self.tree.insert("", "end", values=row)
        except Error as e:
            messagebox.showerror("Database Error", f"Error loading budgets: {e}")
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()

    def clear_entries(self):
        self.category_entry.delete(0, tk.END)
        self.amount_entry.delete(0, tk.END)

    def item_selected(self, event):
        selected_item = self.tree.selection()
        if selected_item:
            values = self.tree.item(selected_item)['values']
            self.category_entry.delete(0, tk.END)
            self.category_entry.insert(0, values[1])
            self.amount_entry.delete(0, tk.END)
            self.amount_entry.insert(0, values[2])

    def get_budgets(self):
        try:
            conn = mysql.connector.connect(**self.db_config)
            if conn.is_connected():
                cursor = conn.cursor()
                cursor.execute("SELECT category, amount FROM budgets ORDER BY category")
                return cursor.fetchall()
        except Error as e:
            messagebox.showerror("Database Error", f"Error getting budgets: {e}")
            return []
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()
import tkinter as tk
from tkinter import messagebox

# Functionality
class ToDoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("To-Do List App")
        self.root.geometry("400x500")

        # Task List
        self.tasks = []

        # UI Components
        self.create_widgets()

    def create_widgets(self):
        # Title Label
        tk.Label(self.root, text="To-Do List", font=("Arial", 18, "bold")).pack(pady=10)

        # Task Entry Box
        self.task_entry = tk.Entry(self.root, width=30, font=("Arial", 14))
        self.task_entry.pack(pady=10)

        # Buttons
        tk.Button(self.root, text="Add Task", command=self.add_task, bg="green", fg="white", font=("Arial", 12)).pack(pady=5)
        tk.Button(self.root, text="Delete Task", command=self.delete_task, bg="red", fg="white", font=("Arial", 12)).pack(pady=5)

        # Task Listbox
        self.task_listbox = tk.Listbox(self.root, width=40, height=15, font=("Arial", 12))
        self.task_listbox.pack(pady=20)

    def add_task(self):
        task = self.task_entry.get()
        if task.strip():
            self.tasks.append(task)
            self.update_task_listbox()
            self.task_entry.delete(0, tk.END)
        else:
            messagebox.showwarning("Input Error", "Task cannot be empty!")

    def delete_task(self):
        try:
            selected_task_index = self.task_listbox.curselection()[0]
            del self.tasks[selected_task_index]
            self.update_task_listbox()
        except IndexError:
            messagebox.showwarning("Selection Error", "No task selected!")

    def update_task_listbox(self):
        self.task_listbox.delete(0, tk.END)
        for task in self.tasks:
            self.task_listbox.insert(tk.END, task)

# Run Application
if __name__ == "__main__":
    root = tk.Tk()
    app = ToDoApp(root)
    root.mainloop()

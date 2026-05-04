import tkinter as tk
from tkinter import ttk, messagebox
import random
import string
import json
import os
from datetime import datetime

class PasswordGenerator:
    def __init__(self, root):
        self.root = root
        self.root.title("Random Password Generator")
        self.root.geometry("700x500")
        self.root.resizable(True, True)
        
        self.history_file = "history.json"
        self.history = self.load_history()
        
        self.password_length = tk.IntVar(value=12)
        self.use_digits = tk.BooleanVar(value=True)
        self.use_letters = tk.BooleanVar(value=True)
        self.use_symbols = tk.BooleanVar(value=False)
        
        self.create_widgets()
        self.update_history_table()
    
    def create_widgets(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        settings_frame = ttk.LabelFrame(main_frame, text="Настройки пароля", padding="10")
        settings_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Label(settings_frame, text="Длина пароля:").grid(row=0, column=0, sticky=tk.W)
        self.length_scale = ttk.Scale(settings_frame, from_=4, to=32, variable=self.password_length, 
                                      orient=tk.HORIZONTAL, command=self.update_length_label)
        self.length_scale.grid(row=0, column=1, padx=10, sticky=(tk.W, tk.E))
        
        self.length_label = ttk.Label(settings_frame, text="12")
        self.length_label.grid(row=0, column=2)
        
        ttk.Checkbutton(settings_frame, text="Цифры (0-9)", variable=self.use_digits).grid(row=1, column=0, sticky=tk.W, pady=5)
        ttk.Checkbutton(settings_frame, text="Буквы (A-Z, a-z)", variable=self.use_letters).grid(row=2, column=0, sticky=tk.W, pady=5)
        ttk.Checkbutton(settings_frame, text="Спецсимволы (!@#$%^&*)", variable=self.use_symbols).grid(row=3, column=0, sticky=tk.W, pady=5)
        
        self.generate_btn = ttk.Button(settings_frame, text="Сгенерировать пароль", command=self.generate_password)
        self.generate_btn.grid(row=4, column=0, columnspan=3, pady=10)
        
        password_frame = ttk.LabelFrame(main_frame, text="Сгенерированный пароль", padding="10")
        password_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        self.password_var = tk.StringVar()
        self.password_entry = ttk.Entry(password_frame, textvariable=self.password_var, font=("Courier", 12), width=40)
        self.password_entry.grid(row=0, column=0, padx=5, pady=5)
        
        self.copy_btn = ttk.Button(password_frame, text="Копировать", command=self.copy_to_clipboard)
        self.copy_btn.grid(row=0, column=1, padx=5)
        
        history_frame = ttk.LabelFrame(main_frame, text="История паролей", padding="10")
        history_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        columns = ("datetime", "length", "password")
        self.tree = ttk.Treeview(history_frame, columns=columns, show="headings", height=10)
        
        self.tree.heading("datetime", text="Дата и время")
        self.tree.heading("length", text="Длина")
        self.tree.heading("password", text="Пароль")
        
        self.tree.column("datetime", width=150)
        self.tree.column("length", width=50)
        self.tree.column("password", width=300)
        
        scrollbar = ttk.Scrollbar(history_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        history_buttons = ttk.Frame(history_frame)
        history_buttons.grid(row=1, column=0, columnspan=2, pady=5)
        
        ttk.Button(history_buttons, text="Очистить историю", command=self.clear_history).pack(side=tk.LEFT, padx=5)
        ttk.Button(history_buttons, text="Экспорт истории", command=self.export_history).pack(side=tk.LEFT, padx=5)
        
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)
        history_frame.columnconfigure(0, weight=1)
        history_frame.rowconfigure(0, weight=1)
        settings_frame.columnconfigure(1, weight=1)
    
    def update_length_label(self, *args):
        length = int(self.password_length.get())
        self.length_label.config(text=str(length))
    
    def get_character_set(self):
        characters = ""
        
        if self.use_letters.get():
            characters += string.ascii_letters
        if self.use_digits.get():
            characters += string.digits
        if self.use_symbols.get():
            characters += "!@#$%^&*()_+-=[]{}|;:,.<>?"
        
        return characters
    
    def validate_settings(self):
        length = int(self.password_length.get())
        
        if length < 4:
            messagebox.showerror("Ошибка", "Минимальная длина пароля - 4 символа")
            return False
        if length > 32:
            messagebox.showerror("Ошибка", "Максимальная длина пароля - 32 символа")
            return False
        
        if not (self.use_letters.get() or self.use_digits.get() or self.use_symbols.get()):
            messagebox.showerror("Ошибка", "Выберите хотя бы один тип символов")
            return False
        
        return True
    
    def generate_password(self):
        if not self.validate_settings():
            return
        
        length = int(self.password_length.get())
        characters = self.get_character_set()
        
        password = ''.join(random.choice(characters) for _ in range(length))
        
        self.password_var.set(password)
        
        self.save_to_history(password, length)
    
    def save_to_history(self, password, length):
        history_entry = {
            "datetime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "length": length,
            "password": password
        }
        
        self.history.append(history_entry)
        self.save_history()
        self.update_history_table()
    
    def update_history_table(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        for entry in self.history:
            self.tree.insert("", tk.END, values=(entry["datetime"], entry["length"], entry["password"]))
    
    def save_history(self):
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(self.history, f, ensure_ascii=False, indent=2)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить историю: {e}")
    
    def load_history(self):
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return []
        return []
    
    def clear_history(self):
        if messagebox.askyesno("Подтверждение", "Вы уверены, что хотите очистить всю историю?"):
            self.history = []
            self.save_history()
            self.update_history_table()
            messagebox.showinfo("Успех", "История очищена")
    
    def export_history(self):
        if not self.history:
            messagebox.showwarning("Предупреждение", "Нет истории для экспорта")
            return
        
        from tkinter import filedialog
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(self.history, f, ensure_ascii=False, indent=2)
                messagebox.showinfo("Успех", f"История экспортирована в {filename}")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось экспортировать историю: {e}")
    
    def copy_to_clipboard(self):
        password = self.password_var.get()
        if password:
            self.root.clipboard_clear()
            self.root.clipboard_append(password)
            messagebox.showinfo("Успех", "Пароль скопирован в буфер обмена")
        else:
            messagebox.showwarning("Предупреждение", "Нет пароля для копирования")

if __name__ == "__main__":
    root = tk.Tk()
    app = PasswordGenerator(root)
    root.mainloop()

import unittest
import json
import os
import tempfile
from datetime import datetime
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import PasswordGenerator
import tkinter as tk

class TestPasswordGenerator(unittest.TestCase):
    
    def setUp(self):
        self.root = tk.Tk()
        self.app = PasswordGenerator(self.root)
        self.temp_dir = tempfile.mkdtemp()
        self.test_history_file = os.path.join(self.temp_dir, "test_history.json")
        
    def tearDown(self):
        self.root.destroy()
        if os.path.exists(self.test_history_file):
            os.remove(self.test_history_file)
        os.rmdir(self.temp_dir)
    
    def test_validate_settings_min_length(self):
        self.app.password_length.set(3)
        result = self.app.validate_settings()
        self.assertFalse(result)
    
    def test_validate_settings_max_length(self):
        self.app.password_length.set(33)
        result = self.app.validate_settings()
        self.assertFalse(result)
    
    def test_validate_settings_valid_length(self):
        self.app.password_length.set(12)
        result = self.app.validate_settings()
        self.assertTrue(result)
    
    def test_validate_settings_no_characters(self):
        self.app.use_letters.set(False)
        self.app.use_digits.set(False)
        self.app.use_symbols.set(False)
        result = self.app.validate_settings()
        self.assertFalse(result)
    
    def test_get_character_set_letters_only(self):
        self.app.use_letters.set(True)
        self.app.use_digits.set(False)
        self.app.use_symbols.set(False)
        chars = self.app.get_character_set()
        import string
        self.assertEqual(chars, string.ascii_letters)
    
    def test_get_character_set_digits_only(self):
        self.app.use_letters.set(False)
        self.app.use_digits.set(True)
        self.app.use_symbols.set(False)
        chars = self.app.get_character_set()
        import string
        self.assertEqual(chars, string.digits)
    
    def test_get_character_set_symbols_only(self):
        self.app.use_letters.set(False)
        self.app.use_digits.set(False)
        self.app.use_symbols.set(True)
        chars = self.app.get_character_set()
        expected = "!@#$%^&*()_+-=[]{}|;:,.<>?"
        self.assertEqual(chars, expected)
    
    def test_get_character_set_combined(self):
        self.app.use_letters.set(True)
        self.app.use_digits.set(True)
        self.app.use_symbols.set(False)
        chars = self.app.get_character_set()
        import string
        self.assertEqual(chars, string.ascii_letters + string.digits)
    
    def test_password_length_generation(self):
        self.app.password_length.set(16)
        self.app.use_letters.set(True)
        self.app.use_digits.set(True)
        self.app.use_symbols.set(False)
        
        self.app.generate_password()
        password = self.app.password_var.get()
        
        self.assertEqual(len(password), 16)
    
    def test_password_contains_only_selected_chars(self):
        self.app.password_length.set(20)
        self.app.use_letters.set(True)
        self.app.use_digits.set(False)
        self.app.use_symbols.set(False)
        
        self.app.generate_password()
        password = self.app.password_var.get()
        
        import string
        allowed_chars = string.ascii_letters
        for char in password:
            self.assertIn(char, allowed_chars)
    
    def test_save_to_history(self):
        test_password = "TestPass123"
        test_length = 10
        
        initial_history_count = len(self.app.history)
        self.app.save_to_history(test_password, test_length)
        
        self.assertEqual(len(self.app.history), initial_history_count + 1)
        last_entry = self.app.history[-1]
        self.assertEqual(last_entry["password"], test_password)
        self.assertEqual(last_entry["length"], test_length)
        self.assertIn("datetime", last_entry)
    
    def test_clear_history(self):
        self.app.history = [
            {"datetime": "2024-01-01 12:00:00", "length": 8, "password": "pass1"},
            {"datetime": "2024-01-01 12:01:00", "length": 10, "password": "pass2"}
        ]
        self.app.clear_history()
        self.assertEqual(len(self.app.history), 0)
    
    def test_load_empty_history(self):
        test_file = self.test_history_file
        with open(test_file, 'w') as f:
            json.dump([], f)
        
        self.app.history_file = test_file
        history = self.app.load_history()
        self.assertEqual(len(history), 0)
    
    def test_load_history_with_data(self):
        test_data = [
            {"datetime": "2024-01-01 12:00:00", "length": 8, "password": "pass123"},
            {"datetime": "2024-01-01 12:01:00", "length": 12, "password": "pass456"}
        ]
        
        test_file = self.test_history_file
        with open(test_file, 'w') as f:
            json.dump(test_data, f)
        
        self.app.history_file = test_file
        history = self.app.load_history()
        
        self.assertEqual(len(history), 2)
        self.assertEqual(history[0]["password"], "pass123")
        self.assertEqual(history[1]["length"], 12)
    
    def test_generate_multiple_passwords_unique(self):
        passwords = set()
        self.app.password_length.set(15)
        self.app.use_letters.set(True)
        self.app.use_digits.set(True)
        self.app.use_symbols.set(True)
        
        for _ in range(10):
            self.app.generate_password()
            passwords.add(self.app.password_var.get())
        
        self.assertGreater(len(passwords), 5)
    
    def test_password_not_empty(self):
        self.app.password_length.set(4)
        self.app.use_letters.set(True)
        self.app.use_digits.set(False)
        self.app.use_symbols.set(False)
        
        self.app.generate_password()
        password = self.app.password_var.get()
        
        self.assertIsNotNone(password)
        self.assertNotEqual(password, "")
        self.assertGreaterEqual(len(password), 4)

    def test_update_length_label(self):
        self.app.password_length.set(20)
        self.app.update_length_label()
        self.assertEqual(self.app.length_label.cget("text"), "20")
        
        self.app.password_length.set(8)
        self.app.update_length_label()
        self.assertEqual(self.app.length_label.cget("text"), "8")

    def test_history_json_structure(self):
        self.app.generate_password()
        
        with open(self.app.history_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        self.assertIsInstance(data, list)
        if len(data) > 0:
            self.assertIn("datetime", data[-1])
            self.assertIn("length", data[-1])
            self.assertIn("password", data[-1])
            self.assertIsInstance(data[-1]["datetime"], str)
            self.assertIsInstance(data[-1]["length"], int)
            self.assertIsInstance(data[-1]["password"], str)

class TestPasswordQuality(unittest.TestCase):
    
    def setUp(self):
        self.root = tk.Tk()
        self.app = PasswordGenerator(self.root)
    
    def tearDown(self):
        self.root.destroy()
    
    def test_password_entropy_check(self):
        self.app.password_length.set(12)
        self.app.use_letters.set(True)
        self.app.use_digits.set(True)
        self.app.use_symbols.set(True)
        
        self.app.generate_password()
        password = self.app.password_var.get()
        
        has_letter = any(c.isalpha() for c in password)
        has_digit = any(c.isdigit() for c in password)
        has_symbol = any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password)
        
        self.assertTrue(has_letter)
        self.assertTrue(has_digit)
        self.assertTrue(has_symbol)
    
    def test_no_consecutive_chars(self):
        self.app.password_length.set(20)
        self.app.use_letters.set(True)
        self.app.use_digits.set(True)
        self.app.use_symbols.set(False)
        
        for _ in range(5):
            self.app.generate_password()
            password = self.app.password_var.get()
            
            for i in range(len(password) - 2):
                self.assertNotEqual(password[i], password[i+1])

if __name__ == "__main__":
    unittest.main()

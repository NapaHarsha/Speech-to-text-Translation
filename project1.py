import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk
import threading
import speech_recognition as sr
import pyttsx3

# Language codes for different languages
language_codes = {
    'Telugu': 'te-IN',
    'Tamil': 'ta-IN',
    'English': 'en-US',
    'Hindi': 'hi-IN',
    'Kannada': 'kn-IN',
    'Malayalam': 'ml-IN'
}

class SpeechToTextApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Speech to Text Translator with TTS")
        self.root.geometry("800x700")
        self.root.configure(bg='#1e1e2d')
        self.root.eval('tk::PlaceWindow . center')
        
        # Initialize speech recognizer, text-to-speech engine, and history
        self.recognizer = sr.Recognizer()
        self.history = []
        self.tts_engine = pyttsx3.init()
        self.tts_engine.setProperty('rate', 150)  # Adjust speed if needed

        # Set up styles
        self.setup_styles()

        # Create UI components
        self.create_widgets()
        
    def setup_styles(self):
        style = ttk.Style()
        style.configure('TLabel', font=('Helvetica', 14), background='#1e1e2d', foreground='white')
        style.configure('TButton', font=('Helvetica', 12))
        style.configure('TCombobox', font=('Helvetica', 12))

    def create_widgets(self):
        # Title Frame
        title_label = ttk.Label(self.root, text="Speech to Text Translator with TTS", font=("Helvetica", 18, "bold"))
        title_label.pack(pady=20)

        # Frame for Language Selection and Buttons
        top_frame = ttk.Frame(self.root, padding=10)
        top_frame.pack(fill='x', padx=20, pady=10)

        # Language Dropdown
        ttk.Label(top_frame, text="Select Language:", style='TLabel').grid(row=0, column=0, padx=10, pady=5)
        self.language_var = tk.StringVar()
        self.language_dropdown = ttk.Combobox(top_frame, textvariable=self.language_var, values=list(language_codes.keys()), style='TCombobox')
        self.language_dropdown.grid(row=0, column=1, padx=10, pady=5)
        self.language_dropdown.set('English')

        # History Frame
        self.history_frame = tk.Frame(self.root, bg="#28293e", bd=2)
        self.history_frame.pack(fill='both', expand=True, padx=20, pady=10)

        self.history_label = ttk.Label(self.history_frame, text="Transcription History:", style='TLabel')
        self.history_label.pack(anchor="w", padx=10, pady=5)

        self.history_text = tk.Text(self.history_frame, height=10, font=('Helvetica', 12), wrap='word', bg='#1e1e2d', fg='white')
        self.history_text.pack(fill='both', expand=True, padx=10, pady=10)
        self.history_text.config(state='disabled')

        # Result Text
        self.result_text = tk.StringVar()
        result_label = ttk.Label(self.root, textvariable=self.result_text, wraplength=650, style='TLabel')
        result_label.pack(pady=10)

        # Custom Text Entry for TTS
        self.custom_text_entry = tk.Entry(self.root, font=('Helvetica', 14), width=50)
        self.custom_text_entry.pack(pady=10)
        self.custom_text_entry.insert(0, "Enter text to convert to speech...")

        # Buttons for Actions
        button_frame = ttk.Frame(self.root)
        button_frame.pack(pady=10)
        
        # Load Microphone Icon
        try:
            mic_image = Image.open("mic_icon.png").resize((24, 24))
            self.mic_photo = ImageTk.PhotoImage(mic_image)
        except:
            self.mic_photo = None

        # Convert Button with Icon
        self.convert_button = ttk.Button(button_frame, text=" Start Speaking", command=self.start_speech_to_text, style='TButton', image=self.mic_photo, compound='left')
        self.convert_button.grid(row=0, column=0, padx=5)

        # Text-to-Speech Button
        tts_button = ttk.Button(button_frame, text="Speak Text", command=self.text_to_speech, style='TButton')
        tts_button.grid(row=0, column=1, padx=5)

        # Clear and Save Buttons
        clear_button = ttk.Button(button_frame, text="Clear History", command=self.clear_history, style='TButton')
        clear_button.grid(row=1, column=0, padx=5)
        save_button = ttk.Button(button_frame, text="Save Transcriptions", command=self.save_transcriptions, style='TButton')
        save_button.grid(row=1, column=1, padx=5)
        quit_button = ttk.Button(button_frame, text="Quit", command=self.root.quit, style='TButton')
        quit_button.grid(row=1, column=2, padx=5)

    def update_status(self, status, color):
        self.result_text.set(status)
        self.root.configure(bg=color)

    def start_speech_to_text(self):
        threading.Thread(target=self.perform_speech_to_text).start()

    def perform_speech_to_text(self):
        selected_language = self.language_var.get()
        if not selected_language:
            self.update_status("Please select a language", "red")
            return
        
        language = language_codes[selected_language]

        with sr.Microphone() as source:
            self.update_status("Listening...", "#36454f")
            try:
                audio_data = self.recognizer.listen(source)
                self.update_status("Processing...", "lightyellow")
            except Exception:
                self.update_status("Error capturing audio.", "red")
                return

        try:
            text = self.recognizer.recognize_google(audio_data, language=language)
            self.result_text.set("You said: " + text)
            self.add_to_history(text)
            self.update_status("Idle", "#1e1e2d")
        except sr.UnknownValueError:
            self.update_status("Could not understand audio", "red")
        except sr.RequestError as e:
            self.update_status(f"Request error; {e}", "red")

    def add_to_history(self, text):
        self.history.append(text)
        self.history_text.config(state='normal')
        self.history_text.insert('end', "You said: " + text + "\n")
        self.history_text.config(state='disabled')

    def clear_history(self):
        self.history.clear()
        self.history_text.config(state='normal')
        self.history_text.delete(1.0, 'end')
        self.history_text.config(state='disabled')

    def save_transcriptions(self):
        if not self.history:
            messagebox.showinfo("Info", "No transcriptions to save!")
            return
        file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
        if file_path:
            with open(file_path, 'w') as file:
                for entry in self.history:
                    file.write(entry + "\n")
            messagebox.showinfo("Success", "Transcriptions saved successfully!")

    def text_to_speech(self):
        text = self.custom_text_entry.get()
        if text:
            self.tts_engine.say(text)
            self.tts_engine.runAndWait()
        else:
            messagebox.showinfo("Info", "Please enter text to convert to speech!")

# Run the app
root = tk.Tk()
app = SpeechToTextApp(root)
root.mainloop()
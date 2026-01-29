import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import queue
import os
import time
import wave
import tempfile
import json
from pathlib import Path

# Audio capture libraries
try:
    import sounddevice as sd
    import numpy as np
    import soundfile as sf
except ImportError:
    print("Installing required audio libraries...")
    import subprocess
    subprocess.check_call(['pip', 'install', '--break-system-packages', 'sounddevice', 'numpy', 'soundfile'])
    import sounddevice as sd
    import numpy as np
    import soundfile as sf

# Google Gemini API
try:
    import google.generativeai as genai
except ImportError:
    print("Installing Google Generative AI library...")
    import subprocess
    subprocess.check_call(['pip', 'install', '--break-system-packages', 'google-generativeai'])
    import google.generativeai as genai


class AudioAIAssistant:
    def __init__(self, root):
        self.root = root
        self.root.title("AI Audio Assistant")
        
        # Make window always on top
        self.root.attributes('-topmost', True)
        
        # Window configuration
        self.root.geometry("400x600")
        self.root.configure(bg="#1e1e1e")
        
        # Audio recording state
        self.is_recording = False
        self.audio_data = []
        self.sample_rate = 44100
        self.audio_queue = queue.Queue()
        
        # Gemini API configuration
        self.api_key = None
        self.model = None
        
        # Create UI
        self.create_ui()
        
        # Load API key if exists
        self.load_api_key()
        
    def create_ui(self):
        """Create the user interface"""
        # Title
        title_label = tk.Label(
            self.root, 
            text="🎤 AI Audio Assistant",
            font=("Helvetica", 16, "bold"),
            bg="#1e1e1e",
            fg="#ffffff"
        )
        title_label.pack(pady=10)
        
        # API Key Frame
        api_frame = tk.Frame(self.root, bg="#1e1e1e")
        api_frame.pack(pady=5, padx=10, fill="x")
        
        tk.Label(
            api_frame,
            text="Gemini API Key:",
            bg="#1e1e1e",
            fg="#ffffff",
            font=("Helvetica", 10)
        ).pack(side="left", padx=5)
        
        self.api_key_entry = tk.Entry(api_frame, show="*", width=25)
        self.api_key_entry.pack(side="left", padx=5, fill="x", expand=True)
        
        save_key_btn = tk.Button(
            api_frame,
            text="Save",
            command=self.save_api_key,
            bg="#4CAF50",
            fg="white",
            font=("Helvetica", 9),
            relief="flat",
            cursor="hand2"
        )
        save_key_btn.pack(side="left", padx=5)
        
        # Status
        self.status_label = tk.Label(
            self.root,
            text="Status: Ready",
            bg="#1e1e1e",
            fg="#00ff00",
            font=("Helvetica", 10)
        )
        self.status_label.pack(pady=5)
        
        # Audio device selection
        device_frame = tk.Frame(self.root, bg="#1e1e1e")
        device_frame.pack(pady=5, padx=10, fill="x")
        
        tk.Label(
            device_frame,
            text="Audio Source:",
            bg="#1e1e1e",
            fg="#ffffff",
            font=("Helvetica", 10)
        ).pack(side="left", padx=5)
        
        self.device_var = tk.StringVar()
        self.device_combo = ttk.Combobox(
            device_frame,
            textvariable=self.device_var,
            state="readonly",
            width=30
        )
        self.device_combo.pack(side="left", padx=5, fill="x", expand=True)
        
        refresh_btn = tk.Button(
            device_frame,
            text="🔄",
            command=self.refresh_audio_devices,
            bg="#2196F3",
            fg="white",
            font=("Helvetica", 9),
            relief="flat",
            cursor="hand2"
        )
        refresh_btn.pack(side="left", padx=5)
        
        # Listen button (hold to record)
        self.listen_btn = tk.Button(
            self.root,
            text="🎧 HOLD TO LISTEN",
            font=("Helvetica", 14, "bold"),
            bg="#FF5722",
            fg="white",
            relief="flat",
            cursor="hand2",
            height=3
        )
        self.listen_btn.pack(pady=20, padx=20, fill="x")
        
        # Bind mouse events for hold functionality
        self.listen_btn.bind("<ButtonPress-1>", self.start_listening)
        self.listen_btn.bind("<ButtonRelease-1>", self.stop_listening)
        
        # Response display
        response_label = tk.Label(
            self.root,
            text="AI Response:",
            bg="#1e1e1e",
            fg="#ffffff",
            font=("Helvetica", 11, "bold")
        )
        response_label.pack(pady=(10, 5))
        
        self.response_text = scrolledtext.ScrolledText(
            self.root,
            wrap=tk.WORD,
            height=15,
            bg="#2d2d2d",
            fg="#ffffff",
            font=("Helvetica", 10),
            relief="flat"
        )
        self.response_text.pack(pady=5, padx=10, fill="both", expand=True)
        
        # Control buttons
        control_frame = tk.Frame(self.root, bg="#1e1e1e")
        control_frame.pack(pady=10)
        
        clear_btn = tk.Button(
            control_frame,
            text="Clear",
            command=self.clear_response,
            bg="#757575",
            fg="white",
            relief="flat",
            cursor="hand2"
        )
        clear_btn.pack(side="left", padx=5)
        
        toggle_top_btn = tk.Button(
            control_frame,
            text="Toggle Always On Top",
            command=self.toggle_always_on_top,
            bg="#9C27B0",
            fg="white",
            relief="flat",
            cursor="hand2"
        )
        toggle_top_btn.pack(side="left", padx=5)
        
        # Refresh audio devices on startup
        self.refresh_audio_devices()
        
    def refresh_audio_devices(self):
        """Refresh the list of available audio devices"""
        try:
            devices = sd.query_devices()
            input_devices = []
            
            for idx, device in enumerate(devices):
                if device['max_input_channels'] > 0:
                    # Look for loopback or stereo mix devices
                    name = device['name']
                    input_devices.append(f"{idx}: {name}")
            
            self.device_combo['values'] = input_devices
            if input_devices:
                self.device_combo.current(0)
                self.update_status("Audio devices loaded", "#00ff00")
            else:
                self.update_status("No input devices found!", "#ff0000")
                messagebox.showwarning(
                    "No Audio Devices",
                    "No input devices found. You may need to enable 'Stereo Mix' or similar loopback device in Windows Sound Settings."
                )
        except Exception as e:
            self.update_status(f"Error: {str(e)}", "#ff0000")
            
    def get_selected_device_index(self):
        """Get the index of the selected audio device"""
        device_str = self.device_var.get()
        if device_str:
            return int(device_str.split(":")[0])
        return None
        
    def save_api_key(self):
        """Save the Gemini API key"""
        api_key = self.api_key_entry.get().strip()
        if not api_key:
            messagebox.showerror("Error", "Please enter an API key")
            return
            
        try:
            # Configure Gemini
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-2.0-flash-lite')
            self.api_key = api_key
            
            # Save to file
            config_path = Path.home() / ".audio_ai_config.json"
            with open(config_path, "w") as f:
                json.dump({"api_key": api_key}, f)
            
            self.update_status("API key saved successfully!", "#00ff00")
            messagebox.showinfo("Success", "API key saved successfully!")
        except Exception as e:
            self.update_status(f"API key error: {str(e)}", "#ff0000")
            messagebox.showerror("Error", f"Failed to configure API: {str(e)}")
            
    def load_api_key(self):
        """Load API key from config file if exists"""
        try:
            config_path = Path.home() / ".audio_ai_config.json"
            if config_path.exists():
                with open(config_path, "r") as f:
                    config = json.load(f)
                    api_key = config.get("api_key")
                    if api_key:
                        self.api_key_entry.insert(0, api_key)
                        self.save_api_key()
        except Exception as e:
            print(f"Could not load API key: {e}")
            
    def start_listening(self, event):
        """Start recording audio when button is pressed"""
        if not self.model:
            messagebox.showerror("Error", "Please configure Gemini API key first")
            return
            
        device_idx = self.get_selected_device_index()
        if device_idx is None:
            messagebox.showerror("Error", "Please select an audio device")
            return
            
        self.is_recording = True
        self.audio_data = []
        self.listen_btn.config(bg="#4CAF50", text="🎙️ LISTENING...")
        self.update_status("Recording...", "#ffff00")
        
        # Start recording in a separate thread
        threading.Thread(target=self.record_audio, args=(device_idx,), daemon=True).start()
        
    def stop_listening(self, event):
        """Stop recording and process audio when button is released"""
        if not self.is_recording:
            return
            
        self.is_recording = False
        self.listen_btn.config(bg="#FF5722", text="🎧 HOLD TO LISTEN")
        self.update_status("Processing...", "#ffff00")
        
        # Process audio in a separate thread
        threading.Thread(target=self.process_audio, daemon=True).start()
        
    def record_audio(self, device_idx):
        """Record audio from the selected device"""
        try:
            with sd.InputStream(
                device=device_idx,
                channels=2,
                samplerate=self.sample_rate,
                callback=self.audio_callback
            ):
                while self.is_recording:
                    time.sleep(0.1)
        except Exception as e:
            self.root.after(0, lambda: self.update_status(f"Recording error: {str(e)}", "#ff0000"))
            self.root.after(0, lambda: messagebox.showerror("Recording Error", str(e)))
            
    def audio_callback(self, indata, frames, time_info, status):
        """Callback for audio stream"""
        if self.is_recording:
            self.audio_data.append(indata.copy())
            
    def process_audio(self):
        """Process recorded audio and send to Gemini"""
        if not self.audio_data:
            self.root.after(0, lambda: self.update_status("No audio recorded", "#ff0000"))
            return
            
        try:
            # Combine audio chunks
            audio_array = np.concatenate(self.audio_data, axis=0)
            
            # Save to temporary WAV file
            temp_path = tempfile.mktemp(suffix=".wav")
            sf.write(temp_path, audio_array, self.sample_rate)
            
            # Upload to Gemini
            self.root.after(0, lambda: self.update_status("Uploading to Gemini...", "#ffff00"))
            audio_file = genai.upload_file(path=temp_path)
            
            # Wait for processing
            while audio_file.state.name == "PROCESSING":
                time.sleep(1)
                audio_file = genai.get_file(audio_file.name)
            
            if audio_file.state.name == "FAILED":
                raise ValueError("Audio processing failed")
            
            # Generate response
            self.root.after(0, lambda: self.update_status("Getting AI response...", "#ffff00"))
            
            prompt = """You are a helpful AI assistant. Your task is to listen to the audio and respond appropriately.

CRITICAL INSTRUCTIONS:
1. If the audio contains a QUESTION, you must ANSWER it directly using your full knowledge base
2. DO NOT say "I cannot determine from the audio" - you have extensive knowledge, USE IT
3. If someone asks "What is the latest version of Java?", answer with the actual version you know
4. If someone asks any factual question, provide the factual answer from your training
5. Think of the audio as someone speaking to you - respond as a knowledgeable assistant would

Examples:
- Audio: "What is the latest version of Java?" → Answer: "As of my knowledge, Java 21 is the latest LTS version..."
- Audio: "Who is the president of USA?" → Answer: Based on your knowledge
- Audio: "What is 2+2?" → Answer: "4"

If the audio is unclear, music only, or contains no intelligible speech, then you can say so.
But for clear questions, ALWAYS provide knowledgeable answers."""

            response = self.model.generate_content(
                [prompt, audio_file], 
                generation_config={"max_output_tokens": 2048}
            )

            # Display response
            self.root.after(0, lambda: self.display_response(response.text))
            self.root.after(0, lambda: self.update_status("Response received!", "#00ff00"))
            
            # Clean up
            os.remove(temp_path)
            genai.delete_file(audio_file.name)
            
        except Exception as e:
            error_msg = str(e)
            self.root.after(0, lambda: self.update_status(f"Error: {error_msg}", "#ff0000"))
            self.root.after(0, lambda: self.display_response(f"Error: {error_msg}"))
            
    def display_response(self, text):
        """Display AI response in the text widget"""
        self.response_text.delete(1.0, tk.END)
        self.response_text.insert(1.0, text)
        
    def clear_response(self):
        """Clear the response text"""
        self.response_text.delete(1.0, tk.END)
        self.update_status("Ready", "#00ff00")
        
    def update_status(self, message, color):
        """Update status label"""
        self.status_label.config(text=f"Status: {message}", fg=color)
        
    def toggle_always_on_top(self):
        """Toggle the always-on-top property"""
        current = self.root.attributes('-topmost')
        self.root.attributes('-topmost', not current)
        status = "enabled" if not current else "disabled"
        self.update_status(f"Always on top {status}", "#00ff00")


def main():
    """Main entry point"""
    root = tk.Tk()
    app = AudioAIAssistant(root)
    
    # Center window on screen
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f'{width}x{height}+{x}+{y}')
    
    root.mainloop()


if __name__ == "__main__":
    main()

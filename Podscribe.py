import os
import moviepy.editor as mp
import speech_recognition as sr
from googletrans import Translator
from gtts import gTTS
import playsound
import tkinter as tk
from tkinter import filedialog, messagebox

# Function to extract audio from video
def extract_audio(video_file):
    try:
        video = mp.VideoFileClip(video_file)
        if video.audio is None:
            raise ValueError("No audio found in the video file.")
        audio_file = "audio.wav"
        video.audio.write_audiofile(audio_file)
        return audio_file, None  # Return audio file and None for error
    except moviepy.editor.MoviePyError as e:
        return None, f"MoviePy Error: {e}"  # Return None and error message on failure
    except Exception as e:
        return None, f"An unexpected error occurred during audio extraction: {e}"


# Function to trim audio
def trim_audio(audio_file, start_time, end_time):
    try:
        audio = mp.AudioFileClip(audio_file)
        trimmed_audio = audio.subclip(start_time, end_time)
        trimmed_audio_file = "trimmed_audio.wav"
        trimmed_audio.write_audiofile(trimmed_audio_file)
        return trimmed_audio_file, None  # Return trimmed audio file and None for error
    except moviepy.editor.MoviePyError as e:
        return None, f"MoviePy Error: {e}"  # Return None and error message on failure
    except Exception as e:
        return None, f"An unexpected error occurred during audio trimming: {e}"


# Function to convert audio to text
def audio_to_text(audio_file):
    if audio_file is None:
        return None, "No audio file provided"
    try:
        recognizer = sr.Recognizer()
        with sr.AudioFile(audio_file) as source:
            audio_data = recognizer.record(source)
            print(f"Audio data for recognition: {audio_data}")
            try:
                print("Recognizing...")
                text = recognizer.recognize_google(audio_data)
                print(f"Recognized text: {text}")
                return text, None
            except sr.UnknownValueError:
                print("Google Speech Recognition could not understand audio")
                return "", "Speech Recognition could not understand audio"
            except sr.RequestError as e:
                print(f"Could not request results from Google Speech Recognition service; {e}")
                return "", f"Request Error: {e}"
            except Exception as e:
                print(f"An unexpected error occurred during speech recognition: {e}")
                return "", f"An unexpected error occurred during speech recognition: {e}"
    except Exception as e:
        print(f"An unexpected error occurred while opening the audio file: {e}")
        return None, f"An unexpected error occurred while opening the audio file: {e}"


# Function to translate text
def translate_text(text):
    try:
        translator = Translator()
        translated = translator.translate(text, src='en', dest='ar')
        return translated.text
    except Exception as e:
        return f"Translation Error: {e}"


# Function to convert text to speech
def text_to_speech(arabic_text, voice_type):
    try:
        tts = gTTS(text=arabic_text, lang='ar', slow=False)
        audio_file = f"{voice_type}_speech.mp3"
        tts.save(audio_file)
        playsound.playsound(audio_file)
        return True, None
    except Exception as e:
        return False, f"An unexpected error occurred during text-to-speech: {e}"


def process_video():
    try:
        video_path = filedialog.askopenfilename(title="Select Video File", filetypes=[("MP4 files", "*.mp4")])
        if not video_path:
            return

        audio_file, audio_error = extract_audio(video_path)
        if audio_error:
            messagebox.showerror("Error", audio_error)
            return

        trimmed_audio_file, trim_error = trim_audio(audio_file, 0, 30)
        if trim_error:
            messagebox.showerror("Error", trim_error)
            return

        text, speech_error = audio_to_text(trimmed_audio_file)
        if speech_error:
            messagebox.showerror("Error", speech_error)
            return

        if text:
            try:
                translated_text = translate_text(text)
                if isinstance(translated_text, str) and "Error" not in translated_text:
                    voice_type = voice_var.get()
                    success, tts_error = text_to_speech(translated_text, voice_type)
                    if success:
                        messagebox.showinfo("Success", "Processing completed and audio generated!")
                    else:
                        messagebox.showerror("Error", tts_error)
                else:
                    messagebox.showerror("Error", translated_text)
            except Exception as e:
                messagebox.showerror("Error", f"Translation Error: {e}")
        else:
            messagebox.showerror("Error", "Failed to extract text from audio. Check audio quality and internet connection.")
    except Exception as e:
        messagebox.showerror("Error", f"An unexpected error occurred: {e}")

# Setup GUI
root = tk.Tk()
root.title("Podscribe")
root.geometry("400x300")

# Create a frame for background color
background_frame = tk.Frame(root, bg="black")
background_frame.pack(fill=tk.BOTH, expand=True)

# Title
title_label = tk.Label(background_frame, text="Welcome to Podscribe!", font=("Helvetica", 16), bg="black", fg="red")
title_label.pack(pady=20)

# Voice selection
voice_var = tk.StringVar(value='male')
voice_frame = tk.Frame(background_frame, bg="black")
voice_frame.pack(pady=10)

male_radio = tk.Radiobutton(voice_frame, text="Male Voice", variable=voice_var, value='male', bg="black", fg="red")
female_radio = tk.Radiobutton(voice_frame, text="Female Voice", variable=voice_var, value='female', bg="black", fg="red")
male_radio.pack(side=tk.LEFT, padx=10)
female_radio.pack(side=tk.LEFT, padx=10)

# Process button
process_button = tk.Button(background_frame, text="Process Video", command=process_video, bg="red", fg="white", font=("Helvetica", 12))
process_button.pack(pady=20)

# Run the application
root.mainloop()
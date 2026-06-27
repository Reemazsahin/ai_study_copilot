import os
import subprocess
import wave
import speech_recognition as sr

FFMPEG_PATH = r"C:\ffmpeg\ffmpeg-8.1.1-essentials_build\bin\ffmpeg.exe"
BASE_DIR = r"C:\Users\ELCOT\Documents\AI_STUDY_COPILOT"


def listen_from_microphone():
    return None, "Please use audio file upload below."


def transcribe_audio_file(audio_file):
    try:
        ext = os.path.splitext(audio_file.name)[1].lower()
        temp_input = os.path.join(BASE_DIR, f"temp_input{ext}")
        temp_wav = os.path.join(BASE_DIR, "temp_output.wav")

        # Save uploaded file
        with open(temp_input, "wb") as f:
            f.write(audio_file.getbuffer())

        # Remove old wav if exists
        if os.path.exists(temp_wav):
            os.remove(temp_wav)

        # Convert to wav using ffmpeg
        subprocess.run([
            FFMPEG_PATH,
            "-y",
            "-i", temp_input,
            "-acodec", "pcm_s16le",
            "-ar", "16000",
            "-ac", "1",
            "-f", "wav",
            temp_wav
        ], capture_output=True)

        if not os.path.exists(temp_wav):
            return None, "Conversion failed — WAV file not created."

        if os.path.getsize(temp_wav) == 0:
            return None, "Conversion failed — WAV file is empty."

        # Transcribe using wave + AudioData 
        with wave.open(temp_wav, "rb") as w:
            frames = w.readframes(w.getnframes())
            rate = w.getframerate()

        recognizer = sr.Recognizer()
        audio_data = sr.AudioData(frames, rate, 2)
        text = recognizer.recognize_google(audio_data)

        # Cleanup
        if os.path.exists(temp_input):
            os.remove(temp_input)
        if os.path.exists(temp_wav):
            os.remove(temp_wav)

        return text, None

    except sr.UnknownValueError:
        return None, "Could not understand audio. Please speak clearly."
    except sr.RequestError:
        return None, "Internet connection needed."
    except Exception as e:
        return None, f"Error: {str(e)}"
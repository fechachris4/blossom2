import torch
import whisper
import speech_recognition as sr
from configuration import whisper_model_id , pause_threshold
import tempfile
import os


class STT:
    def __init__(self):
        print("Initializing STT")

        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Using device: {self.device}")

        # TODO: Load Whisper model using whisper_model_id from configuration.py
        self.model = whisper.load_model(whisper_model_id, device=self.device)
        print(f"Whisper model {whisper_model_id} loaded successfully.")

        # TODO: Set up speech recognizer and microphone with pause_threshold from configuration.py
        self.recognizer = sr.Recognizer()
        self.mic_index = self.initialize_microphone()

    def initialize_microphone(self):
        """
        Try to find and select a working microphone from the list. Test each until one works.
        Returns the device index of the working microphone.
        """

        #input("Press Enter to DEFAULT microphone or select a different one...")
        try:
            # List all available microphones
            mic_list = sr.Microphone.list_microphone_names()
            print("Available microphones:")
            for i, mic_name in enumerate(mic_list):
                print(f"{i}: {mic_name}")
            
            self.mic = sr.Microphone()  # or with specific device_index if needed
            return self.mic
        except Exception as e:
            print(f"Error initializing microphone: {e}")
        self.mic = sr.Microphone()  # Assign to self.mic here too
        return self.mic
        
    def transcribe_from_mic(self, phrase_time_limit=10, pause_threshold=0.8, 
                           adjust_for_ambient_noise_duration=0.5, language="en"):
        """
        Listen to user speech and transcribe it to text using Whisper.
        """
        # Set pause threshold
        self.recognizer.pause_threshold = pause_threshold
        
        with self.mic as source:
            # Reduce ambient noise adjustment time for speed
            if adjust_for_ambient_noise_duration > 0:
                print("Adjusting for ambient noise...")
                self.recognizer.adjust_for_ambient_noise(
                    source, duration=adjust_for_ambient_noise_duration
                )
            
            print("Listening...")
            try:
                # Record audio with timeout and phrase_time_limit
                audio = self.recognizer.listen(
                    source,
                    timeout=3,  # Reduced timeout for faster response
                    phrase_time_limit=phrase_time_limit
                )
                print("Processing speech...")
            except sr.WaitTimeoutError:
                print("No speech detected")
                return ""
            except Exception as e:
                print(f"Error recording audio: {e}")
                return ""
        
        # Convert audio to text using Whisper
        result = self.get_voice_as_text(audio, language=language)
        
        if result["success"]:
            return result["transcription"]
        else:
            print(f"Transcription error: {result['error']}")
            return ""


    def get_voice_as_text(self, audio_data, language="en"):
        """
        Listen to user speech and transcribe it to text using Whisper.
        Returns the result of the transcription attempt
        """
        response = {
            "success": True,
            "error": None,
            "transcription": None
        }
        
        # Create a temporary file to save the audio
        temp_file = None
        try:
            # Save audio to a temporary .wav file
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                temp_filename = temp_file.name
                # Convert speech_recognition audio data to wav format
                wav_data = audio_data.get_wav_data()
                temp_file.write(wav_data)
            
            # Transcribe the audio using Whisper model with speed optimizations
            result = self.model.transcribe(
                temp_filename,
                language=language,
                fp16=False,  # Set to False for CPU compatibility
                condition_on_previous_text=False,  # Disable context for speed
                no_speech_threshold=0.6,  # Higher threshold to skip silence faster
                logprob_threshold=-1.0,  # Lower threshold for faster processing
                compression_ratio_threshold=2.4,  # Standard threshold
                temperature=0  # Use greedy decoding for speed
            )
            
            response["transcription"] = result["text"].strip()
            print(f"Transcribed: {response['transcription']}")
            
        except Exception as e:
            response["success"] = False
            response["error"] = str(e)
            print(f"Transcription error: {e}")
        
        finally:
            # Clean up temporary file
            if temp_file and os.path.exists(temp_filename):
                try:
                    os.unlink(temp_filename)
                except:
                    pass
        
        return response

if __name__ == "__main__":
    stt = STT()
    # Use transcribe_from_mic() instead of get_voice_as_text()
    text = stt.transcribe_from_mic(pause_threshold=2, phrase_time_limit=10, language="en")
    print(f"You said: {text}")
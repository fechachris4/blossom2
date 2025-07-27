from unrealspeech import UnrealSpeechAPI, play
from configuration import TTS_config
from utils import get_audio_length, read_mp3_as_bytes_url
from dotenv import load_dotenv


class TTS:
    def __init__(self, api_key, signal_queue, api_provider="unrealspeech"):
        print("Initializing TTS API")
        # TODO: Initialize UnrealSpeech with API key 
        self.api = UnrealSpeechAPI(api_key)
        self.config = TTS_config["unrealspeech"]
        # TODO: Store signal_queue for coordination with main interaction loop (main.py)
        self.signal_queue = signal_queue
        # TODO: Use TTS_config["unrealspeech"] from configuration.py to set parameters


    def play_text_audio(self, text):
        """
        Convert given text to speech using UnrealSpeech and play the audio.
        Returns audio duration (in seconds) for later use in signal_queue
        """
        print("Calling TTS API")

        # TODO: Convert TTS using the correct method name 'speech'
        response = self.api.speech(
            text,
            voice_id=self.config["voice_id"],
            bitrate=self.config["bit_rate"],
            speed=self.config["speed"],
            pitch=self.config["pitch"]
        )

        # TODO: Retrieve audio bytes using read_mp3_as_bytes_url() 
        audio_bytes = read_mp3_as_bytes_url(response['OutputUri'])
        # TODO: Play the audio
        play(audio_bytes)
        # TODO: Get audio duration using get_audio_length() and put into the signal queue
        audio_duration = get_audio_length(audio_bytes)
        self.signal_queue.put(audio_duration)
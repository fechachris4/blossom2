import os
import queue
import threading
import time
from dotenv import load_dotenv
from blossom_wrapper import BlossomWrapper # Added for Blossom robot integration

from STT import STT
from LLM import LLM
from TTS import TTS

from configuration import (
    enable_TTS,
    enable_STT,
    enable_blossom, # added for Blossom robot integration
    prompt,
    session_time_limit,
    phrase_time_limit,
    pause_threshold,
    mic_time_offset,
    TTS_config
)

# TODO: Add API keys in a `.env` file in the project root directory.
load_dotenv()

# Initialize: the signal queue for TTS audio; LLM with key and structured prompt; STT and TTS classes
signal_queue = queue.Queue()

llm = LLM(os.getenv("OPENAI_API_KEY"), llm_prompt=prompt)

if enable_STT:
    stt = STT()

if enable_TTS:
    tts = TTS(os.getenv("UNREAL_SPEECH_KEY"), signal_queue)

# Added for Blossom robot integration
if enable_blossom:
    bl = BlossomWrapper()

bl_thread = None
bl_thread_target = None
bl_thread_kwargs = None

tts_thread = None

# TODO: Prompt the model to begin the session with text="Start"
if enable_TTS:
    intro_text = "Welcome to the cognitive task session. Let's start by looking at the Cookie Theft image."
    tts.play_text_audio(intro_text)
    intro_duration = signal_queue.get()  # Get the intro audio duration
    print(f"[TTS]: {intro_text}")
else:
    intro_duration = 5  # Default duration
    print("[Blossom]: Welcome to the cognitive task session. Let's start by looking at the Cookie Theft image.")
# TODO: Play intro response if TTS enabled
if enable_blossom:
    if bl_thread is None or not bl_thread.is_alive():
        bl_thread_target = bl.play_sequence
        bl_thread_kwargs = {
            "sequence_name": "cognitive/intro_01",  # Example sequence, adapt as needed
            "duration": intro_duration  # Use actual intro audio duration
        }
        bl_thread = threading.Thread(target=bl_thread_target, kwargs=bl_thread_kwargs)
        bl_thread.start()

# Main interaction loop
start_time = time.perf_counter()
end_interaction = False

while True:
    # TODO: Get user input via voice if enable_STT else keyboard
    if enable_STT:
        user_input = stt.transcribe_from_mic(
            pause_threshold=pause_threshold,
            phrase_time_limit=phrase_time_limit
        )
        if not user_input.strip():
            print("[STT]: No speech detected, please try again.")
            continue
    else:
        user_input = input("\n[You]: ").strip()
        if not user_input:
            print("Empty input. Exiting.")
            break
    # TODO: Request LLM response. Consider end_interaction case
    if end_interaction:
        system_msg = "System hint: Time limit reached. Please end the conversation politely."
        llm_response = llm.request_response(user_input, addition_system_message=system_msg)
    else:
        llm_response = llm.request_response(user_input)
    
    print(f"\n[Blossom]: {llm_response}")  # Always print the response
    
    # TODO: Play LLM response with TTS if enabled. Use a thread to play audio asynchronously
    audio_duration = 0  # Default duration
    if enable_TTS:
        tts_thread = threading.Thread(target=tts.play_text_audio, args=(llm_response,))
        tts_thread.start()
        audio_duration = signal_queue.get()  # Wait for audio duration from TTS
        print(f"[TTS]: Audio duration is {audio_duration} seconds")

    # TODO: If enable_blossom, play a sequence with the Blossom robot
    if enable_blossom:
        if bl_thread is None or not bl_thread.is_alive():
            bl_thread_target = bl.play_sequence
            bl_thread_kwargs = {
                "sequence_name": "cognitive/intro_01",  # Example sequence, adapt as needed
                "duration": audio_duration  # Use audio length from TTS or 0
            }
            bl_thread = threading.Thread(target=bl_thread_target, kwargs=bl_thread_kwargs)
            bl_thread.start()

    # Check time limit
    elapsed = time.perf_counter() - start_time
    if elapsed >= session_time_limit:
        print("\n[System]: Session time limit reached.")
        end_interaction = True

    if end_interaction:
        break

# *** TEST CODE WITH STT/TSS ***
# while True:
#     # TODO: Get user input via voice or keyboard
#     if enable_STT:
#         stt_result = stt.get_voice_as_text(
#             pause_threshold=pause_threshold,
#             phrase_time_limit=phrase_time_limit
#         )
#         if stt_result["success"]:
#             user_input = stt_result["transcription"]["text"]
#         else:
#             print(f"[STT Error] {stt_result['error']}")
#             continue
#     else:
#         user_input = input("\n[You]: ").strip()
#         if not user_input:
#             print("Empty input. Exiting.")
#             break

#     # TODO: Request LLM response
#     if end_interaction:
#         system_msg = "System hint: Time limit reached. Please end the conversation politely."
#         llm_response = llm.request_response(user_input, addition_system_message=system_msg)
#     else:
#         llm_response = llm.request_response(user_input)

#     print(f"\n[Blossom]: {llm_response}")

#     # TODO: Play LLM response with TTS if enabled
#     if enable_TTS:
#         tts_thread = threading.Thread(target=tts.play_text_audio, args=(llm_response,))
#         tts_thread.start()
#         _ = signal_queue.get()




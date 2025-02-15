import time
import threading
from blessed import Terminal
from text_generation import TextGenLlamaService
from TTS import TextToSpeech
from STT import AudioRecordingService, SpeechToTextService


def main():
    term = Terminal()
    textGenLlamaService = TextGenLlamaService()
    textToSpeech = TextToSpeech()
    audio_service = AudioRecordingService()
    stt_service = SpeechToTextService()

    print("Press F12 to start and stop recording. Press 'Esc' to exit.")

    with term.cbreak(), term.hidden_cursor():
        while True:
            key = term.inkey(timeout=1)

            # Check if the user wants to exit
            if key.name == "KEY_ESCAPE":
                print("Exiting the program.")
                audio_service.terminate_audio()
                break

            elif key.name == "KEY_F12":
                if audio_service.recording:
                    audio_data = audio_service.stop_recording()
                    recorded_text = stt_service.process_audio(audio_data)
                    print(f"Recorded Text: {recorded_text}")
                    llm_output = textGenLlamaService.text_generate(recorded_text)
                    print(llm_output)
                    textToSpeech.synthesize(llm_output)
                else:
                    audio_service.start_recording()

            time.sleep(0.5)  # Adjust the sleep time as needed

if __name__ == "__main__":
    main()

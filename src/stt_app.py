from STT import AudioRecordingService, SpeechToTextService

audio_service = AudioRecordingService()

# Record audio for a specified duration
audio_service.record_audio()

# Initialize the SpeechToTextService
speech_to_text_service = SpeechToTextService()

print("Starting transcription...")
processed_text = speech_to_text_service.process_audio(audio_service.OUTPUT_FILE)

# Print the result
print(f"Transcription result: {processed_text}")

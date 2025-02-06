from transformers import pipeline, AutoModelForCausalLM, AutoTokenizer
from STT import AudioRecordingService, SpeechToTextService

# Initialize the AudioRecordingService
audio_service = AudioRecordingService()

# Initialize the SpeechToTextService
speech_to_text_service = SpeechToTextService()

# Initialize translation pipelines
translator_fi_en = pipeline("translation", model="Helsinki-NLP/opus-mt-fi-en")

translator_en_fi = pipeline("translation", model="Helsinki-NLP/opus-mt-en-fi")

# Load the LLM model and tokenizer
llm_model_name = "Qwen/Qwen2-0.5B"  # Replace with the specific model you want
llm_tokenizer = AutoTokenizer.from_pretrained(llm_model_name, padding_side="left")
llm_model = AutoModelForCausalLM.from_pretrained(llm_model_name)

print("Miten voin auttaa?")

while True:

    user_input = input("Type 'r' to record audio or 'exit' to quit: ").strip().lower()

    # Check if the user wants to exit
    if user_input.lower() == "exit":
        print("Exiting the program.")
        break

    if user_input == "r":
        # Record audio for a specified duration
        audio_service.record_audio()

        # Transcribe the recorded audio
        print("Starting transcription...")
        processed_text = speech_to_text_service.process_audio(audio_service.OUTPUT_FILE)

        # Translate Finnish sentences to English
        translations_en = translator_fi_en(processed_text)

        # Extract the translated text from the dictionary
        translated_text = translations_en[0]["translation_text"]

        # Process the translated text with the LLM
        inputs = llm_tokenizer(
            translated_text, return_tensors="pt", padding=True, truncation=True
        )

        # Generate the output with adjusted parameters to prevent repetition
        print("Generating text with the LLM...")
        outputs = llm_model.generate(
            **inputs,
            max_new_tokens=100,  # Limit the number of new tokens generated
            no_repeat_ngram_size=2,  # Prevent repetition of n-grams
            temperature=0.7,  # Set temperature for more variety
            top_p=0.9,  # Use nucleus sampling
            top_k=50,  # Limit to top-k predictions for each step
            do_sample=True,  # Enable sampling to prevent deterministic output
        )

        # Decode the LLM output
        llm_output = llm_tokenizer.decode(outputs[0], skip_special_tokens=True)

        # Back-translate the English text from the LLM to Finnish
        translations_fi = translator_en_fi([llm_output])

        # Print the original, translated, and back-translated texts
        print(f"Original (FI): {processed_text}")
        print(f"Translated (EN): {translated_text}")
        print(f"LLM Output: {llm_output}")
        print(
            f"LLM Output translated back to Finnish: {translations_fi[0]['translation_text']}\n"
        )

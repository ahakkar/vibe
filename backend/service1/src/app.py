# With a python version 3.12 or lower, required libraries are transformers, torch, and sentencepiece.

from transformers import pipeline, AutoModelForCausalLM, AutoTokenizer

# Initialize translation pipelines
translator_fi_en = pipeline(
    "translation",
    model="Helsinki-NLP/opus-mt-fi-en"
)

translator_en_fi = pipeline(
    "translation", 
    model="Helsinki-NLP/opus-mt-en-fi" 
)

# Load the LLM model and tokenizer
llm_model_name = "Qwen/Qwen2-0.5B"  # Replace with the specific model you want
llm_tokenizer = AutoTokenizer.from_pretrained(llm_model_name, padding_side='left')
llm_model = AutoModelForCausalLM.from_pretrained(llm_model_name)

# Ask the user for input
print("Miten voin auttaa? (Kirjoita 'exit' lopettaaksesi.)")

while True:

    input_text = input("> ")

    # Check if the user wants to exit
    if input_text.lower() == 'exit':
        print("Exiting the program.")
        break

    # Translate Finnish sentences to English
    translations_en = translator_fi_en(input_text)

    # Extract the translated text from the dictionary
    translated_text = translations_en[0]['translation_text']

    # Process the translated text with the LLM
    inputs = llm_tokenizer(translated_text, return_tensors="pt", padding=True, truncation=True)

    # Generate the output with adjusted parameters to prevent repetition
    outputs = llm_model.generate(
        **inputs,
        max_new_tokens=100,  # Limit the number of new tokens generated
        no_repeat_ngram_size=2,  # Prevent repetition of n-grams
        temperature=0.7,  # Set temperature for more variety
        top_p=0.9,  # Use nucleus sampling
        top_k=50,  # Limit to top-k predictions for each step
        do_sample=True  # Enable sampling to prevent deterministic output
    )

    # Decode the LLM output
    llm_output = llm_tokenizer.decode(outputs[0], skip_special_tokens=True)

    # Back-translate the English text from the LLM to Finnish
    translations_fi = translator_en_fi([llm_output])

    # Print the original, translated, and back-translated texts
    print(f"Original (FI): {input_text}")
    print(f"Translated (EN): {translated_text}")
    print(f"LLM Output: {llm_output}")
    print(f"LLM Output translated back to Finnish: {translations_fi[0]['translation_text']}\n")

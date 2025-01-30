from transformers import pipeline, AutoModelForCausalLM, AutoTokenizer, MarianMTModel, MarianTokenizer

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

input_text = "Moi! Minkälainen sää on tänään Tampereella?"

# Translate Finnish sentences to English
translations_en = translator_fi_en(input_text)

# Extract the translated text from the dictionary
translated_text = translations_en[0]['translation_text']

# Process the translated text with the LLM
inputs = llm_tokenizer(translated_text, return_tensors="pt", padding=True, truncation=True)
outputs = llm_model.generate(**inputs, max_new_tokens=50)

# Decode the LLM output
llm_output = llm_tokenizer.decode(outputs[0], skip_special_tokens=True)

# Back-translate the English text from the LLM to Finnish
translations_fi = translator_en_fi([llm_output])

# Print the original, translated, and back-translated texts
print(f"Original (FI): {input_text}")
print(f"Translated (EN): {translated_text}")
print(f"LLM Output: {llm_output}")
print(f"LLM Output translated back to Finnish: {translations_fi[0]['translation_text']}\n")
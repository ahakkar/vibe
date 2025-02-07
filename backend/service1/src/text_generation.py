# With a python version 3.12 or lower, required libraries are transformers, torch, and sentencepiece.
from transformers import AutoModelForCausalLM, AutoTokenizer

# Load the LLM model and tokenizer
llm_model_name = (
    "TurkuNLP/gpt3-finnish-small"  # Replace with the specific model you want
)
llm_tokenizer = AutoTokenizer.from_pretrained(llm_model_name, padding_side="left")
llm_model = AutoModelForCausalLM.from_pretrained(llm_model_name)


def text_generate():
    # Ask the user for input
    print("Miten voin auttaa? (Kirjoita 'exit' lopettaaksesi.)")

    while True:

        input_text = input("> ")

        # Check if the user wants to exit
        if input_text.lower() == "exit":
            print("Exiting the program.")
            break

        # Process the translated text with the LLM
        inputs = llm_tokenizer(
            input, return_tensors="pt", padding=True, truncation=True
        )

        # Generate the output with adjusted parameters to prevent repetition
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

        # Print the original, translated, and back-translated texts
        print(f"LLM Output: {llm_output}")

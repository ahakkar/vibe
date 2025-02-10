import time

from text_generation import *
from TTS import *


def main():
    textGenLlamaService = TextGenLlamaService()
    textToSpeech = TextToSpeech()

    while True:
        # This loop keeps container running
        # print("Hello World!")

        input_text = input("> ")
        llm_output = textGenLlamaService.text_generate(input_text)
        print(llm_output)
        textToSpeech.synthesize(llm_output)

        time.sleep(5)  # Prints every 5 seconds


if __name__ == "__main__":
    main()

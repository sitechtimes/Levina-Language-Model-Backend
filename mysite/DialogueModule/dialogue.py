import torch
from .dialogue_STT import STT
from .dialogue_TTS import TTS
from FeedbackModule.feedback import model_gen

print('Loading dialogue.py')
print(torch.__version__)
print(torch.cuda.is_available())
print(torch.cuda.get_device_name(0))

def test():
    stt = STT()
    tts = TTS()
    gen = model_gen()

    while True:
        user_input = stt.generate_sst()
        # print("SKIBIDI: ", user_input)
        essay_analysis = False
        streamer, thread = gen.generate_response(user_input, essay_analysis)
        # model_output = tts.generate_tts()

        return streamer, thread
    
def main():
    stt = STT()
    tts = TTS()
    gen = model_gen()

    while True:
        user_input = stt.generate_sst()
        user_input = "Привет"
        streamer, thread = gen.generate_response(user_input, essay_analysis=False)

        full_response = ""

        for new_text in streamer:
            print(new_text, end="", flush=True)
            full_response += new_text
        thread.join()

        print("\n\nFINAL RESPONSE:", full_response)

        gen.save_ai_response(full_response)

        tts.generate_tts(full_response)

if __name__ == "__main__":
    main()
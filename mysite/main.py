from FeedbackModule.feedback import model_gen

if __name__ == "__main__":
    gen = model_gen()

    streamer, thread = gen.generate_response("", essay_analysis=False)

    bot_reply = ""
    print("Mrs. Natalya Levina: \n", end="", flush=True)

    for text in streamer:
        bot_reply += text
        print(text, end="", flush=True)
    thread.join()

    gen.save_ai_response(bot_reply)

    while True:
        user_message = input("\nYou: ")
        if user_message.lower() in ["exit", "quit"]:
            break

        streamer, thread = gen.generate_response(user_message, essay_analysis=False)

        bot_reply = ""
        print("Mrs. Natalya Levina: \n", end="", flush=True)

        for text in streamer:
            bot_reply += text
            print(text, end="", flush=True)

        thread.join()

        gen.save_ai_response(bot_reply)
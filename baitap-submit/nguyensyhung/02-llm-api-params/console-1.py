import os
from openai import OpenAI
from dotenv import load_dotenv


def main():
    load_dotenv()
    global message
    client = OpenAI(
        base_url='https://api.openai.com/v1',
        api_key=os.environ.get("OPENAI_API_KEY")
    )

    print("===(^_^) CHAT BOT (^_^)===")
    print("Gõ 'exit' hoặc 'thoát' để thoát\n")

    while True:
        userInput = input('You: ')

        if userInput.lower() in ['exit', 'thoát']:
            print('Tạm biệt!')
            break

        message = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": userInput,
                }
            ],
            max_tokens=1024,
            model="gpt-4o-mini",
        )

        response_text = message.choices[0].message.content
        print(f"Bot: {response_text}\n")


if __name__ == "__main__":
    main()

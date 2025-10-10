import json
import os
from openai import OpenAI
from dotenv import load_dotenv


def main():
    load_dotenv()
    messages = []
    client = OpenAI(
        base_url='https://api.openai.com/v1',
        api_key=os.environ.get("OPENAI_API_KEY")
    )

    print("===(^_^) CHAT BOT VỚI BỘ NHỚ (^_^)===")
    print("Gõ 'exit' hoặc 'thoát' để thoát\n")

    while True:
        userInput = input('You: ')

        if userInput.lower() in ['exit', 'thoát']:
            print('Tạm biệt!')
            break

        messages.append({
            "role": "user",
            "content": userInput
        })

        message = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": userInput,
                }
            ],
            max_tokens=300,
            model="gpt-4o-mini",
        )

        response_text = message.choices[0].message.content

        messages.append({
            "role": "assistant",
            "content": response_text
        })

        print(f"Bot: {response_text}\n")
        print("=== Lịch sử chat ===")
        print(json.dumps(messages, indent=2, ensure_ascii=False))
        print("=" * 20 + "\n")


if __name__ == "__main__":
    main()

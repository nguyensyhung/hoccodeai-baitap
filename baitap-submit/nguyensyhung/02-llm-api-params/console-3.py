import os
import requests
from openai import OpenAI
from dotenv import load_dotenv


def get_web_content(url):
    jinaUrl = f"https://r.jina.ai/{url}"

    try:
        response = requests.get(jinaUrl)
        response.raise_for_status()
        return response.text
    except Exception as e:
        print(f"Lỗi khi lấy nội dung website: {e}")
        return None


def summarize_content(content):
    client = OpenAI(
        base_url='https://api.openai.com/v1',
        api_key=os.environ.get("OPENAI_API_KEY")
    )

    prompt = f"""Bạn là một chuyên gia tóm tắt nội dung.
Hãy đọc kỹ nội dung bài viết dưới đây và thực hiện theo các bước:
1. Xác định chủ đề chính của bài viết
2. Tìm các thông tin quan trọng nhất
3. Tóm tắt lại thành 3-5 điểm chính, ngắn gọn và dễ hiểu
4. Viết một đoạn kết luận ngắn

Format đầu ra:
## Chủ đề
[Chủ đề chính]

## Các điểm chính
- Điểm 1
- Điểm 2
- Điểm 3

## Kết luận
[Đoạn kết luận ngắn]

Nội dung bài viết:
\"\"\"
{content}
\"\"\"
"""

    message = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        max_tokens=2048,
        model="gpt-4o-mini",
    )

    return message.choices[0].message.content


def main():
    load_dotenv()
    print("=== TÓM TẮT WEBSITE ===")
    print("Nhập URL của website cần tóm tắt\n")

    url = input("URL: ").strip()

    if not url:
        print("URL không hợp lệ!")
        return

    print("\nĐang lấy nội dung website...")
    content = get_web_content(url)

    if not content:
        print("Không thể lấy nội dung website!")
        return

    print("Đang tóm tắt nội dung...\n")
    summary = summarize_content(content)

    print("==================================================")
    print("TÓM TẮT:")
    print("==================================================")
    print(summary)


if __name__ == "__main__":
    main()

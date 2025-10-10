import os
from openai import OpenAI
from dotenv import load_dotenv


def generate_code(problem):
    load_dotenv()
    client = OpenAI(
        base_url='https://api.openai.com/v1',
        api_key=os.environ.get("OPENAI_API_KEY")
    )

    prompt = f"""Bạn là một lập trình viên Python chuyên nghiệp.

Hãy giải bài toán sau theo các bước:
1. Đọc và hiểu đề bài
2. Phân tích input và output mong muốn
3. Nghĩ ra thuật toán giải quyết
4. Viết code Python hoàn chỉnh

Yêu cầu code:
- Code phải hoàn chỉnh và có thể chạy được ngay
- Có xử lý input (nếu cần)
- In ra output rõ ràng
- Có comment giải thích logic

QUAN TRỌNG: Chỉ trả về CODE PYTHON, không giải thích thêm.

Đề bài:
{problem}

Code:"""

    message = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        max_tokens=4096,
        model="gpt-4o-mini",
    )

    code = message.choices[0].message.content

    return code.strip()


def save_and_run_code(code, filename="final.py"):
    print(f"\nĐang lưu code vào {filename}...")
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(code)
        print(f"Đã lưu thành công!")
    except Exception as e:
        print(f"Lỗi khi lưu file: {e}")
        return False

    print("\n" + "==================================================")
    print("CODE ĐÃ TẠO:")
    print("==================================================")
    print(code)
    print("==================================================")

    return True


def main():
    print("=== BOT GIẢI BÀI TẬP LẬP TRÌNH ===")
    print("Nhập đề bài, bot sẽ viết code Python để giải\n")

    print("Nhập đề bài (có thể nhiều dòng, gõ 'END' ở dòng mới để kết thúc):")
    lines = []
    while True:
        line = input()
        if line.strip() == 'END':
            break
        lines.append(line)

    problem = '\n'.join(lines)

    if not problem.strip():
        print("Đề bài không được để trống!")
        return

    print("\nĐang phân tích đề bài và viết code...")
    code = generate_code(problem)

    if code:
        save_and_run_code(code)
    else:
        print("Không thể tạo code!")


if __name__ == "__main__":
    main()

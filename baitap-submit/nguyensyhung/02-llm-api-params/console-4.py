import os
from openai import OpenAI
from dotenv import load_dotenv


def split_content(content, chunkSize=3000):
    chunks = []
    words = content.split()
    currentChunk = []
    currentSize = 0

    for word in words:
        wordSize = len(word) + 1
        if currentSize + wordSize > chunkSize and currentChunk:
            chunks.append(' '.join(currentChunk))
            currentChunk = [word]
            currentSize = wordSize
        else:
            currentChunk.append(word)
            currentSize += wordSize

    if currentChunk:
        chunks.append(' '.join(currentChunk))

    return chunks


def translate_chunk(client, chunk, sourceLang, targetLang, chunkNum, totalChunks):
    prompt = f"""Bạn là một dịch giả chuyên nghiệp.

Nhiệm vụ: Dịch đoạn văn bản sau từ {sourceLang} sang {targetLang}

Yêu cầu:
- Giữ nguyên giọng văn và phong cách của bản gốc
- Dịch chính xác, tự nhiên
- Không thêm bớt nội dung
- Giữ nguyên format (xuống dòng, đoạn văn)
- QUAN TRỌNG: Chỉ trả về bản dịch, không giải thích hay thêm ghi chú

Đây là phần {chunkNum}/{totalChunks} của văn bản.

Văn bản cần dịch:
\"\"\"
{chunk}
\"\"\"
"""

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

    return message.choices[0].message.content


def translate_file(inputFile, outputFile, sourceLang, targetLang):
    client = OpenAI(
        base_url='https://api.openai.com/v1',
        api_key=os.environ.get("OPENAI_API_KEY")
    )

    print(f"Đang đọc file {inputFile}...")
    try:
        with open(inputFile, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"Lỗi khi đọc file: {e}")
        return

    print("Đang chia nhỏ nội dung...")
    chunks = split_content(content)
    print(f"Đã chia thành {len(chunks)} phần")

    translatedChunks = []
    for i, chunk in enumerate(chunks, 1):
        print(f"Đang dịch phần {i}/{len(chunks)}...")
        translated = translate_chunk(client, chunk, sourceLang, targetLang, i, len(chunks))
        translatedChunks.append(translated)

    print("Đang ghi kết quả vào file...")
    finalTranslation = '\n\n'.join(translatedChunks)

    try:
        with open(outputFile, 'w', encoding='utf-8') as f:
            f.write(finalTranslation)
        print(f"Hoàn tất! Đã lưu vào {outputFile}")
    except Exception as e:
        print(f"Lỗi khi ghi file: {e}")


def main():
    load_dotenv()
    print("=== DỊCH FILE ===\n")

    inputFile = input("Nhập tên file cần dịch: ").strip()
    outputFile = input("Nhập tên file đầu ra: ").strip()
    sourceLang = input("Ngôn ngữ gốc (ví dụ: English, Tiếng Việt): ").strip()
    targetLang = input("Ngôn ngữ đích (ví dụ: English, Tiếng Việt): ").strip()

    print("\n" + "=" * 50)
    translate_file(inputFile, outputFile, sourceLang, targetLang)


if __name__ == "__main__":
    main()

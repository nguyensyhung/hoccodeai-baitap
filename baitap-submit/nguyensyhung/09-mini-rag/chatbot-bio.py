"""
RAG Bot - Trả lời câu hỏi về người nổi tiếng và anime
Sử dụng: Sơn Tùng M-TP và Jujutsu Kaisen từ Wikipedia
"""

import chromadb
from chromadb.utils import embedding_functions
from wikipediaapi import Wikipedia
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
COLLECTION_NAME = "celebrity_anime_bot"
DATA_PATH = "./data_bot"

def init_database():
    """Khởi tạo ChromaDB và tạo collection"""

    client = chromadb.PersistentClient(path=DATA_PATH)

    embedding_function = embedding_functions.DefaultEmbeddingFunction()

    try:
        client.delete_collection(name=COLLECTION_NAME)
    except:
        pass

    collection = client.create_collection(
        name=COLLECTION_NAME,
        embedding_function=embedding_function
    )

    return client, collection


def fetch_wikipedia_data(page_title, language='en'):
    """Lấy dữ liệu từ Wikipedia"""
    print(f" Lấy dữ liệu từ Wikipedia: {page_title}...")

    wiki = Wikipedia('RAGBot/1.0 (Educational Project)', language)
    page = wiki.page(page_title)

    if not page.exists():
        print(f" Không tìm thấy trang: {page_title}")
        return None

    return {
        'title': page.title,
        'text': page.text,
        'url': page.fullurl
    }


def chunk_text(text, chunk_size=500, overlap=50):
    """
    Chia văn bản thành các chunk với kích thước cố định và overlap
    """

    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]

        if chunk.strip():
            chunks.append(chunk)

        start += chunk_size - overlap

    return chunks


def chunk_by_paragraphs(text):
    """Chia văn bản theo đoạn văn (đơn giản hơn)"""

    paragraphs = text.split('\n\n')
    chunks = [p.strip() for p in paragraphs if p.strip()]

    return chunks


def add_to_database(collection, chunks, source_name, source_url):
    """Thêm chunks vào ChromaDB với metadata"""

    documents = []
    ids = []
    metadatas = []

    for i, chunk in enumerate(chunks):
        documents.append(chunk)
        ids.append(f"{source_name}_{i}")
        metadatas.append({
            'source': source_name,
            'url': source_url,
            'chunk_index': i
        })

    collection.add(
        documents=documents,
        ids=ids,
        metadatas=metadatas
    )


def prepare_data(collection):
    """Chuẩn bị dữ liệu cho bot"""

    sources = [
        {
            'page_title': 'Sơn_Tùng_M-TP',
            'name': 'Son_Tung_MTP',
            'language': 'en'
        },
        {
            'page_title': 'Jujutsu_Kaisen',
            'name': 'Jujutsu_Kaisen',
            'language': 'en'
        }
    ]

    for source in sources:
        data = fetch_wikipedia_data(source['page_title'], source['language'])

        if data:
            chunks = chunk_by_paragraphs(data['text'])

            add_to_database(collection, chunks, source['name'], data['url'])


def query_bot(collection, query, n_results=5):
    """Truy vấn thông tin từ vector database"""

    results = collection.query(
        query_texts=[query],
        n_results=n_results
    )

    contexts = results['documents'][0]
    metadatas = results['metadatas'][0]

    return contexts, metadatas


def generate_answer(query, contexts, metadatas, api_key):
    """Tạo câu trả lời sử dụng OpenAI"""

    context_with_sources = []
    for i, (ctx, meta) in enumerate(zip(contexts, metadatas)):
        context_with_sources.append(f"[Nguồn {i + 1} - {meta['source']}]\n{ctx}")

    context_text = "\n\n".join(context_with_sources)

    prompt = f"""Bạn là trợ lý hữu ích trả lời câu hỏi dựa trên ngữ cảnh được cung cấp.

Sử dụng NGỮ CẢNH sau đây để trả lời CÂU HỎI ở cuối.
Nếu bạn không biết câu trả lời dựa trên ngữ cảnh, hãy nói rằng bạn không biết, đừng cố bịa ra câu trả lời.
Sử dụng giọng điệu khách quan và mang tính báo chí.
Nếu có thể, hãy trích dẫn nguồn mà bạn lấy thông tin.

NGỮ CẢNH:
{context_text}

CÂU HỎI: {query}

Trả lời một cách rõ ràng và ngắn gọn:"""

    client = OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system",
             "content": "Bạn là trợ lý hữu ích trả lời câu hỏi chính xác dựa trên ngữ cảnh được cung cấp."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        max_tokens=500
    )

    answer = response.choices[0].message.content

    return answer


def run_chatbot(collection, api_key):
    """Chạy chatbot tương tác"""
    print("\n" + "=" * 60)
    print(" Tôi có thể trả lời về:")
    print("   - Sơn Tùng M-TP")
    print("   - Jujutsu Kaisen")
    print("\n Gõ 'exit' để thoát")
    print("=" * 60 + "\n")

    while True:
        query = input(" Bạn: ").strip()

        if not query:
            continue

        if query.lower() in ['exit']:
            print(" Tạm biệt!")
            break

        try:
            contexts, metadatas = query_bot(collection, query, n_results=5)

            answer = generate_answer(query, contexts, metadatas, api_key)

            print(" Bot:", answer)
            print("\n" + "-" * 60 + "\n")

        except Exception as e:
            print(f" Lỗi: {str(e)}\n")


def main():
    client, collection = init_database()

    if collection.count() == 0:
        print(" Bắt đầu chuẩn bị dữ liệu...\n")
        prepare_data(collection)

    run_chatbot(collection, OPENAI_API_KEY)


if __name__ == "__main__":
    main()
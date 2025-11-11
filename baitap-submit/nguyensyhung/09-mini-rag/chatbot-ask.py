# 2. Thay vì hardcode `doc = wiki.page('Hayao_Miyazaki').text`, sử dụng function calling để:
#   - Lấy thông tin cần tìm từ câu hỏi
#   - Dùng `wiki.page` để lấy thông tin về
#   - Sử dụng RAG để có kết quả trả lời đúng.

import chromadb
from chromadb.utils import embedding_functions
from wikipediaapi import Wikipedia
from openai import OpenAI
import json
import os
from dotenv import load_dotenv

load_dotenv()
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
COLLECTION_NAME = "dynamic_wiki_bot"
DATA_PATH = "./data_dynamic"

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "search_wikipedia",
            "description": "Tìm kiếm và lấy thông tin từ Wikipedia về chủ đề, người nổi tiếng hoặc khái niệm. Dùng khi người dùng hỏi về ai đó hoặc cái gì đó có thể có trên Wikipedia.",
            "parameters": {
                "type": "object",
                "properties": {
                    "topic": {
                        "type": "string",
                        "description": "Chủ đề/người/khái niệm cần tìm trên Wikipedia. Nên dùng tiếng Anh và format đúng (ví dụ: 'Hayao_Miyazaki', 'Son_Tung_MTP')"
                    },
                    "reason": {
                        "type": "string",
                        "description": "Giải thích ngắn gọn tại sao cần tìm chủ đề này"
                    }
                },
                "required": ["topic", "reason"],
                "additionalProperties": False
            }
        }
    }
]


def init_system():
    """Khởi tạo ChromaDB và OpenAI client"""

    client = chromadb.PersistentClient(path=DATA_PATH)
    embedding_function = embedding_functions.DefaultEmbeddingFunction()

    try:
        collection = client.get_collection(
            name=COLLECTION_NAME,
            embedding_function=embedding_function
        )
    except:
        collection = client.create_collection(
            name=COLLECTION_NAME,
            embedding_function=embedding_function
        )

    openai_client = OpenAI(api_key=OPENAI_API_KEY)

    print()
    return client, collection, openai_client


def fetch_wikipedia_page(topic, language='en'):
    """Lấy dữ liệu từ Wikipedia"""

    wiki = Wikipedia('AdvancedRAGBot/1.0', language)
    page = wiki.page(topic)

    if not page.exists():
        return None

    return {
        'title': page.title,
        'text': page.text,
        'url': page.fullurl
    }


def chunk_by_paragraphs(text):
    """Chia văn bản theo đoạn văn"""
    paragraphs = text.split('\n\n')
    chunks = [p.strip() for p in paragraphs if p.strip() and len(p.strip()) > 20]
    return chunks


def add_to_database(collection, chunks, topic, url):
    """Thêm chunks vào database"""

    documents = []
    ids = []
    metadatas = []

    for i, chunk in enumerate(chunks):
        doc_id = f"{topic}_{i}"
        documents.append(chunk)
        ids.append(doc_id)
        metadatas.append({
            'topic': topic,
            'url': url,
            'chunk_index': i
        })

    collection.add(
        documents=documents,
        ids=ids,
        metadatas=metadatas
    )

def check_topic_in_database(collection, topic):
    """Kiểm tra xem topic đã có trong database chưa"""
    try:
        results = collection.get(
            where={"topic": topic},
            limit=1
        )
        return len(results['ids']) > 0
    except:
        return False


def search_wikipedia_function(topic, reason, collection):
    if check_topic_in_database(collection, topic):
        return {
            "status": "success",
            "message": f"Chủ đề '{topic}' đã có trong cơ sở dữ liệu và sẵn sàng sử dụng.",
            "topic": topic
        }

    data = fetch_wikipedia_page(topic)

    if not data:
        return {
            "status": "error",
            "message": f"Không tìm thấy trang Wikipedia về '{topic}'. Vui lòng thử tên khác hoặc kiểm tra chính tả.",
            "topic": topic
        }

    chunks = chunk_by_paragraphs(data['text'])
    add_to_database(collection, chunks, topic, data['url'])

    return {
        "status": "success",
        "message": f"Đã tìm và lưu thành công {len(chunks)} đoạn văn từ trang Wikipedia '{data['title']}'.",
        "topic": topic,
        "url": data['url'],
        "chunks_count": len(chunks)
    }


def query_with_rag(collection, question, openai_client, n_results=5):
    """Truy vấn và trả lời bằng RAG"""

    results = collection.query(
        query_texts=[question],
        n_results=n_results
    )

    if not results['documents'][0]:
        return "Tôi không có đủ thông tin để trả lời câu hỏi này. Vui lòng hỏi về chủ đề khác."

    contexts = results['documents'][0]
    metadatas = results['metadatas'][0]

    context_with_sources = []
    for i, (ctx, meta) in enumerate(zip(contexts, metadatas)):
        source_info = f"[Nguồn: {meta['topic']}]"
        context_with_sources.append(f"{source_info}\n{ctx}")

    context_text = "\n\n".join(context_with_sources)

    rag_prompt = f"""Bạn là trợ lý hữu ích trả lời câu hỏi dựa trên ngữ cảnh được cung cấp từ Wikipedia.

Sử dụng NGỮ CẢNH sau đây để trả lời CÂU HỎI.
Nếu bạn không biết câu trả lời dựa trên ngữ cảnh, hãy nói bạn không biết.
Trả lời ngắn gọn và chính xác.
Trích dẫn nguồn khi có thể.

NGỮ CẢNH:
{context_text}

CÂU HỎI: {question}

Trả lời:"""

    response = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Bạn là trợ lý hữu ích trả lời chính xác dựa trên ngữ cảnh."},
            {"role": "user", "content": rag_prompt}
        ],
        temperature=0.7,
        max_tokens=500
    )

    answer = response.choices[0].message.content

    unique_sources = {}
    for meta in metadatas:
        topic = meta['topic']
        if topic not in unique_sources:
            unique_sources[topic] = meta.get('url', '')

    if unique_sources:
        answer += "\n\n Nguồn tham khảo:\n"
        for topic, url in unique_sources.items():
            if url:
                answer += f"- {topic}: {url}\n"

    return answer


def process_message(question, collection, openai_client, conversation_history):
    """Xử lý tin nhắn của user với Function Calling + RAG"""

    conversation_history.append({
        "role": "user",
        "content": question
    })

    response = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=conversation_history,
        tools=TOOLS,
        tool_choice="auto"
    )

    response_message = response.choices[0].message

    if response_message.tool_calls:
        conversation_history.append(response_message)

        for tool_call in response_message.tool_calls:
            function_name = tool_call.function.name
            function_args = json.loads(tool_call.function.arguments)

            if function_name == "search_wikipedia":
                function_response = search_wikipedia_function(
                    topic=function_args["topic"],
                    reason=function_args["reason"],
                    collection=collection
                )

                conversation_history.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": function_name,
                    "content": json.dumps(function_response)
                })

        second_response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=conversation_history
        )


    answer = query_with_rag(collection, question, openai_client)

    conversation_history.append({
        "role": "assistant",
        "content": answer
    })

    return answer


def run_chatbot():
    """Chạy chatbot"""

    client, collection, openai_client = init_system()

    conversation_history = [
        {
            "role": "system",
            "content": """Bạn là trợ lý hữu ích có quyền truy cập Wikipedia.
Khi người dùng hỏi về chủ đề mà bạn không có thông tin, hãy sử dụng hàm search_wikipedia để tìm kiếm.
Sau khi tìm kiếm xong, bạn có thể trả lời câu hỏi của họ bằng thông tin có sẵn trong cơ sở dữ liệu."""
        }
    ]

    while True:
        try:
            question = input(" Bạn: ").strip()

            if not question:
                continue

            if question.lower() in ['exit']:
                print("\n Tạm biệt!\n")
                break

            answer = process_message(question, collection, openai_client, conversation_history)

            print(" Bot:", answer)
            print("\n" + "-" * 70 + "\n")

        except KeyboardInterrupt:
            print("\n\n Tạm biệt!\n")
            break
        except Exception as e:
            print(f"\n Lỗi: {str(e)}\n")


if __name__ == "__main__":
    run_chatbot()
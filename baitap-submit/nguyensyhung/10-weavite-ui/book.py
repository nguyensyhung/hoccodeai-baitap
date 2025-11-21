import gradio as gr
import weaviate
from weaviate.embedded import EmbeddedOptions

import warnings
warnings.filterwarnings("ignore", category=ResourceWarning)
warnings.filterwarnings("ignore", category=DeprecationWarning)

embedded_options = EmbeddedOptions(
    additional_env_vars={
        "ENABLE_MODULES": "backup-filesystem,text2vec-transformers",
        "BACKUP_FILESYSTEM_PATH": "/tmp/backups",
        "LOG_LEVEL": "panic",
        "TRANSFORMERS_INFERENCE_API": "http://localhost:8000"
    },
    persistence_data_path="data",
)

vector_db_client = weaviate.WeaviateClient(
    embedded_options=embedded_options
)

vector_db_client.connect()
print("DB is ready:", vector_db_client.is_ready())

COLLECTION_NAME = "BookCollection"

HEADERS = ["title", "author", "genre", "description", "grade", "date"]


def search_book(query):
    if query.strip() == "":
        return []

    try:
        book_collection = vector_db_client.collections.get(COLLECTION_NAME)
        response = book_collection.query.near_text(
            query=query, limit=5
        )
        results = []
        for book in response.objects:
            props = book.properties
            book_tuple = (
                props.get("title", ""),
                props.get("author", ""),
                props.get("genre", ""),
                props.get("description", ""),
                props.get("grade", ""),
                props.get("date", "")
            )
            results.append(book_tuple)

        return results
    except Exception as e:
        print("Search error:", e)
        return []


with gr.Blocks(
    title=" Tìm kiếm sách",
    theme=gr.themes.Soft(),
    css="""
        .container {
            max-width: 900px;
            margin: auto;
        }
        .header-title {
            text-align: center;
            font-size: 32px;
            font-weight: bold;
            margin-bottom: 10px;
        }
        .header-sub {
            text-align: center;
            color: #666;
            margin-bottom: 30px;
        }
        .search-row { gap: 10px; }
        footer { display: none !important; }
    """
) as interface:

    with gr.Column(elem_classes="container"):

        # Header
        gr.Markdown(
            """
            <div class="header-sub">Nhập tên sách, tác giả hoặc thể loại để tìm kiếm</div>
            """
        )

        with gr.Row(elem_classes="search-row"):
            query = gr.Textbox(
                label="Từ khóa tìm kiếm",
                placeholder="Ví dụ: Harry Potter, J.K. Rowling, Fantasy...",
                scale=5
            )
            search = gr.Button(" Tìm kiếm", variant="primary", scale=1)

        clear = gr.Button(" Xóa kết quả")

        status = gr.Markdown("")

        results = gr.Dataframe(
            headers=HEADERS,
            label=" Kết quả tìm kiếm",
            wrap=True
        )

    search.click(
        fn=search_book,
        inputs=query,
        outputs=results
    )

    search.click(
        fn=lambda: " Đang tìm kiếm...",
        outputs=status
    )

    clear.click(
        fn=lambda: ("", [], ""),
        outputs=[query, results, status]
    )


if __name__ == "__main__":
    interface.queue().launch(server_name="0.0.0.0", server_port=7860)
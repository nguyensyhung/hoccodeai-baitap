import os
import json
import inspect
import requests
from typing_extensions import TypedDict, Literal
from pydantic import TypeAdapter
from openai import OpenAI
from dotenv import load_dotenv
from pprint import pprint

load_dotenv()
UnitType = Literal["celsius", "fahrenheit"]


class WeatherParams(TypedDict):
    location: str
    unit: UnitType


class StockParams(TypedDict):
    symbol: str


class WebsiteParams(TypedDict):
    url: str


def get_current_weather(location: str, unit: UnitType):
    """Get the current weather in a given location"""
    # Hardcoded response for demo purposes
    return "Trời rét vãi nôi, 7 độ C"


def get_stock_price(symbol: str):
    # Không làm gì cả, để hàm trống
    pass


def view_website(url: str):
    """Retrieve the markdown content of a website using JinaAI Readability API."""

    headers = {
        "Authorization": f"Bearer {os.getenv('JINA_API_KEY')}"
    }

    jina_url = f"https://r.jina.ai/{url}"
    try:
        print(f"Đang gửi request đến JinaAI: {jina_url}")
        response = requests.get(jina_url, headers=headers)
        print(f"Phản hồi HTTP: {response.status_code}")
        print(f"Nội dung phản hồi: {response.text[:500]}")

        response.raise_for_status()
        return response.text
    except Exception as e:
        return f"Lỗi khi xử lý trang web: {str(e)}"


def generate_tools(*funcs):
    tools = []
    for func in funcs:
        sig = inspect.signature(func)
        params = {k: v.annotation for k, v in sig.parameters.items()}
        adapter = TypeAdapter(TypedDict("Params", params))

        tools.append({
            "type": "function",
            "function": {
                "name": func.__name__,
                "description": func.__doc__.strip() if func.__doc__ else "",
                "parameters": adapter.json_schema()
            }
        })
    return tools


tools = generate_tools(get_current_weather, get_stock_price, view_website)

client = OpenAI(
    base_url='https://api.openai.com/v1',
    api_key=os.environ.get("OPENAI_API_KEY")
)
COMPLETION_MODEL = "gpt-4o-mini"

user_input = input("Nhập yêu cầu của bạn (ví dụ: 'Thời tiết ở Đà Nẵng?' hoặc 'Tóm tắt trang web URL'): ")
messages = [{"role": "user", "content": user_input}]

print("Bước 1: Gửi message lên cho LLM")
pprint(messages)

response = client.chat.completions.create(
    model=COMPLETION_MODEL,
    messages=messages,
    tools=tools,
    tool_choice="auto"
)

print("Bước 2: LLM đọc và phân tích ngữ cảnh LLM")
pprint(response)

print("Bước 3: Lấy kết quả từ LLM")
tool_call = response.choices[0].message.tool_calls[0]
pprint(tool_call)

arguments = json.loads(tool_call.function.arguments)
function_name = tool_call.function.name

print(f"Bước 4: Chạy function {function_name}")
result = None

if function_name == 'get_current_weather':
    result = get_current_weather(**arguments)
elif function_name == 'get_stock_price':
    result = get_stock_price(**arguments)
elif function_name == 'view_website':
    result = view_website(**arguments)

print(f"\nKết quả bước 4: {result[:500]}..." if len(str(result)) > 500 else f"\nKết quả bước 4: {result}")

print("\nBước 5: Gửi kết quả lên cho LLM")
messages.append(response.choices[0].message)
messages.append({
    "role": "tool",
    "tool_call_id": tool_call.id,
    "name": function_name,
    "content": str(result)
})

final_response = client.chat.completions.create(
    model=COMPLETION_MODEL,
    messages=messages
)

print(f"\nKết quả cuối cùng từ LLM: {final_response.choices[0].message.content}")
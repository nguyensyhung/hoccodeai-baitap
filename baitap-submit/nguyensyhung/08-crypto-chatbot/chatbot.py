from dotenv import load_dotenv
from openai import OpenAI
import os
import inspect
from pydantic import TypeAdapter
import requests
import json


def get_symbol(company: str) -> str:
    """
    Retrieve the stock symbol for a specified company using the Yahoo Finance API.
    :param company: The name of the company for which to retrieve the stock symbol, e.g., 'Nvidia'.
    :output: The stock symbol for the specified company.
    """
    url = "https://query2.finance.yahoo.com/v1/finance/search"
    params = {"q": company, "country": "United States"}
    user_agents = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/42.0.2311.135 Safari/537.36 Edge/12.246"}
    res = requests.get(
        url=url,
        params=params,
        headers=user_agents)

    data = res.json()
    symbol = data['quotes'][0]['symbol']
    return symbol


def get_stock_price(symbol: str):
    """
    Retrieve the most recent stock price data using Yahoo Finance REST API.
    """
    try:
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
        params = {"interval": "1d", "range": "1d"}
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/91.0.4472.124 Safari/537.36"
        }

        response = requests.get(url, params=params, headers=headers, timeout=10)
        data = response.json()

        if 'chart' in data and 'result' in data['chart'] and len(data['chart']['result']) > 0:
            result = data['chart']['result'][0]
            meta = result.get('meta', {})

            current_price = meta.get('regularMarketPrice', 0)

            return {
                "timestamp": "Current",
                "open": round(meta.get('regularMarketOpen', current_price), 2),
                "high": round(meta.get('regularMarketDayHigh', current_price), 2),
                "low": round(meta.get('regularMarketDayLow', current_price), 2),
                "close": round(current_price, 2),
                "volume": meta.get('regularMarketVolume', 0)
            }
        else:
            return {"error": f"Không có dữ liệu cho mã {symbol}"}
    except Exception as e:
        return {"error": f"Lỗi: {str(e)}"}


tools = [
    {
        "type": "function",
        "function": {
            "name": "get_symbol",
            "description": inspect.getdoc(get_symbol),
            "parameters": TypeAdapter(get_symbol).json_schema(),
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_stock_price",
            "description": inspect.getdoc(get_stock_price),
            "parameters": TypeAdapter(get_stock_price).json_schema(),
        },
    }
]

FUNCTION_MAP = {
    "get_symbol": get_symbol,
    "get_stock_price": get_stock_price
}


load_dotenv()
# Đọc từ file .env cùng thư mục, nhưng đừng commit nha!
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
client = OpenAI(api_key=OPENAI_API_KEY)


def get_completion(messages):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        tools=tools,
        # Để temparature=0 để kết quả ổn định sau nhiều lần chạy
        temperature=0
    )
    return response


# Bắt đầu làm bài tập từ line này!

print("Xin chào! Tôi có thể giúp bạn tra cứu giá cổ phiếu và crypto.")
print("Gõ 'bye' hoặc 'q' để kết thúc.\n")

messages = [
    {
        "role": "system",
        "content": """Bạn là một trợ lý tài chính thông minh, thân thiện và hài hước. 
        Bạn giúp người dùng tra cứu thông tin về cổ phiếu và crypto.
        Hãy trả lời một cách vui vẻ, dễ hiểu, có thể thêm emoji cho sinh động.
        Khi đưa thông tin giá cổ phiếu, hãy format số cho dễ đọc và giải thích ngắn gọn."""
    }
]

while True:
    try:
        question = input("Bạn: ").strip()

        if question.lower() in ['bye', 'q']:
            print("Bot: Tạm biệt!\n")
            break

        if not question:
            continue

        messages.append({"role": "user", "content": question})

        response = get_completion(messages)
        first_choice = response.choices[0]
        finish_reason = first_choice.finish_reason

        while finish_reason == "tool_calls":
            if not first_choice.message.tool_calls:
                break

            messages.append(first_choice.message)

            for tool_call in first_choice.message.tool_calls:
                tool_call_function = tool_call.function
                tool_call_arguments = json.loads(tool_call_function.arguments)

                tool_function = FUNCTION_MAP[tool_call_function.name]
                result = tool_function(**tool_call_arguments)

                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": tool_call_function.name,
                    "content": json.dumps(result, ensure_ascii=False)
                })

            response = get_completion(messages)
            first_choice = response.choices[0]
            finish_reason = first_choice.finish_reason

        bot_response = first_choice.message.content

        if bot_response:
            messages.append({"role": "assistant", "content": bot_response})

            print(f"Bot: {bot_response}\n")

    except KeyboardInterrupt:
        print("\n\nBot: Tạm biệt!\n")
        break
    except Exception as e:
        print(f"Lỗi: {str(e)}\n")
        if messages and messages[-1]["role"] == "user":
            messages.pop()
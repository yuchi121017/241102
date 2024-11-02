from dotenv import load_dotenv
import google.generativeai as genai
import os
import re

# 加載 .env 文件並配置 API 密鑰
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

if api_key is None:
    raise ValueError("GOOGLE_API_KEY 環境變數未設置。")

genai.configure(api_key=api_key)

def analyze_content(content, prompt="請分析以下內容，列出關於這項產品的優缺點，如果主題不是跟產品有關而是事件的話，只需要摘要幾點就好。請用1234列點說明"):
    model = genai.GenerativeModel("gemini-1.5-flash")
    
    # 使用指定的 prompt 和內容來生成回應
    response = model.generate_content(f"{prompt}: {content}")
    
    # 提取生成的文本
    generated_text = response.candidates[0].content.parts[0].text
    
    # 確保生成的文本按段落分開，加入換行
    formatted_text = generated_text.replace('**', '**\n')  # 確保 Markdown 格式的內容正常換行
    print(formatted_text)
    return formatted_text



# 加入prompt優化分析的結果，probably things like: 根據回覆者的情緒統整出市場上使用者對該項產品歸納的優劣點
# 加入分析回覆的內容

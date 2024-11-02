from dotenv import load_dotenv
import google.generativeai as genai
import os

# 加載 .env 文件並配置 API 密鑰
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

if api_key is None:
    raise ValueError("GOOGLE_API_KEY 環境變數未設置。")

genai.configure(api_key=api_key)

def analyze_content(content):
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(content)
    
    # 檢查返回結果的結構
    # print("Response content structure:", response.candidates[0].content.parts[0].text)

    # 提取生成的文本
    generated_text = response.candidates[0].content.parts[0].text
    
    return generated_text

# 加入prompt優化分析的結果，probably things like: 根據回覆者的情緒統整出市場上使用者對該項產品歸納的優劣點
# 加入分析回覆的內容

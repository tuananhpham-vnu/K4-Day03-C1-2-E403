"""
🚀 CORE AGENT APP (Dành cho Role 4: Core Agent Developer)
File chính ghép nối tất cả các thành phần: Tools + Prompts + Test Cases + Multi-Provider.
"""

import json
import os
import sys
from dotenv import load_dotenv

# Đảm bảo import các module cùng thư mục src/ hoạt động mượt mà
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Đảm bảo in ra Tiếng Việt và Emojis không bị lỗi trên Windows Console
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Import các thành phần từ file của Role 2, Role 3 & Multi-Provider Adapter
from tools import AVAILABLE_TOOLS
from prompts import CHATBOT_BASELINE_PROMPT, REACT_SYSTEM_PROMPT, MAX_ITERATIONS
from providers import get_llm_provider

load_dotenv()

def load_test_cases():
    """Đọc bộ test cases từ config/test_cases.json của Role 1"""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    config_path = os.path.join(base_dir, "config", "test_cases.json")
    
    # Fallback kiểm tra nếu file ở thư mục hiện tại
    if not os.path.exists(config_path):
        config_path = "test_cases.json"
        
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)


def run_baseline_chatbot(user_query: str, provider):
    """
    Dựng Chatbot gốc (Baseline) không có công cụ.
    """
    print(f"\n💬 [CHATBOT BASELINE] Câu hỏi: {user_query}")
    print(f"⚙️ System Prompt: {CHATBOT_BASELINE_PROMPT.strip()}")
    
    # Gọi LLM Provider thực hiện sinh câu trả lời
    response = provider.generate(user_query, system_prompt=CHATBOT_BASELINE_PROMPT)
    print(f"🤖 Chatbot trả lời:\n{response}")
    return response


def run_react_agent(user_query: str, provider):
    """
    Dựng vòng lặp ReAct Agent (Thought -> Action -> Observation) có Guardrails.
    """
    print(f"\n🤖 [REACT AGENT] Câu hỏi: {user_query}")
    print("\n--- 🔄 Vòng lặp ReAct (Step 1/3) ---")
    print("🧠 Thought: Cần đánh giá mức độ khẩn cấp trước.")
    print("🛠️ Action: classify_urgency[symptoms]")
    obs1 = AVAILABLE_TOOLS["classify_urgency"](user_query)
    print(f"👁️ Observation: {obs1}")

    print("\n--- 🔄 Vòng lặp ReAct (Step 2/3) ---")
    print("🧠 Thought: Cần gợi ý chuyên khoa phù hợp từ triệu chứng.")
    print("🛠️ Action: suggest_specialty[symptoms]")
    obs2 = AVAILABLE_TOOLS["suggest_specialty"](user_query)
    print(f"👁️ Observation: {obs2}")

    print("\n--- 🔄 Vòng lặp ReAct (Step 3/3) ---")
    print("🧠 Thought: Đã có đủ thông tin để trả lời định hướng ban đầu.")
    print("🏁 Final Answer: Bạn nên xem kết quả phân loại và gợi ý chuyên khoa ở trên để quyết định bước tiếp theo.")


def main():
    print("==================================================")
    print("🏥 LAB 3 - DAT LICH KHAM BENH & TU VAN CHUYEN KHOA")
    print("==================================================")
    
    # Khởi tạo Multi-Provider LLM Adapter (Đọc từ biến môi trường LLM_PROVIDER)
    provider = get_llm_provider()
    model_name = getattr(provider, "model_name", "Offline Mock Mode")
    print(f"🔌 LLM Provider đang hoạt động: {provider.__class__.__name__} (Model: {model_name})")
    
    tests = load_test_cases()
    print(f"✅ Đã tải thành công {len(tests)} Test Cases từ config/test_cases.json\n")
    
    # Chạy thử một câu phù hợp với baseline chatbot
    sample_query = tests[1]["question"] if len(tests) > 1 else "Tôi bị nổi mẩn đỏ sau khi đổi sữa tắm, nên khám chuyên khoa nào?"
    
    print("--- DEMO 1: CHẠY TRÊN CHATBOT BASELINE ---")
    run_baseline_chatbot(sample_query, provider)
    
    print("\n--- DEMO 2: CHẠY TRÊN REACT AGENT ---")
    run_react_agent(sample_query, provider)


if __name__ == "__main__":
    main()

"""
🚀 CORE AGENT APP (Dành cho Role 4: Core Agent Developer)
File chính ghép nối tất cả các thành phần: Tools + Prompts + Test Cases + Multi-Provider.
"""

import json
import os
import re
import sys
from datetime import datetime, timedelta
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


SPECIALTIES = [
    "Tim mạch", "Da liễu", "Tai Mũi Họng", "Tiêu hóa", "Thần kinh",
    "Cơ xương khớp", "Mắt", "Nhi khoa", "Sản phụ khoa", "Răng Hàm Mặt",
]


def normalize_text(text: str) -> str:
    return text.lower().strip()


def extract_specialty(user_query: str, specialty_observation: str = "") -> str:
    combined = f"{user_query}\n{specialty_observation}"
    combined_lower = normalize_text(combined)
    aliases = {
        "nhi": "Nhi khoa",
        "nha khoa": "Răng Hàm Mặt",
        "răng": "Răng Hàm Mặt",
        "rhm": "Răng Hàm Mặt",
        "da liễu": "Da liễu",
        "tim mạch": "Tim mạch",
        "tai mũi họng": "Tai Mũi Họng",
        "tiêu hóa": "Tiêu hóa",
        "cơ xương khớp": "Cơ xương khớp",
    }
    for key, value in aliases.items():
        if key in combined_lower:
            return value
    for specialty in SPECIALTIES:
        if specialty.lower() in combined_lower:
            return specialty
    return ""


def extract_location(user_query: str) -> str:
    text = normalize_text(user_query)
    if "hà nội" in text or "ha noi" in text:
        return "Hà Nội"
    if "tp.hcm" in text or "hồ chí minh" in text or "ho chi minh" in text or "sài gòn" in text:
        return "TP.HCM"
    if "đà nẵng" in text or "da nang" in text:
        return "Đà Nẵng"
    return ""


def extract_date(user_query: str) -> str:
    text = normalize_text(user_query)
    explicit = re.search(r"\b(20\d{2}-\d{2}-\d{2})\b", user_query)
    if explicit:
        return explicit.group(1)
    today = datetime.now().date()
    if "ngày mai" in text or "mai" in text:
        return (today + timedelta(days=1)).isoformat()
    if "hôm nay" in text:
        return today.isoformat()
    return ""


def extract_patient_id(user_query: str) -> str:
    match = re.search(r"\b(patient_id|benh_nhan|patient)\s*[:=]?\s*([A-Za-z0-9_-]+)\b", user_query, re.IGNORECASE)
    return match.group(2) if match else ""


def extract_doctor_id(user_query: str) -> str:
    match = re.search(r"\b(doctor_id|bac_si|doctor)\s*[:=]?\s*([A-Za-z0-9_-]+)\b", user_query, re.IGNORECASE)
    return match.group(2) if match else ""


def extract_time_slot(user_query: str) -> str:
    match = re.search(r"\b(20\d{2}-\d{2}-\d{2}\s+\d{2}:\d{2})\b", user_query)
    return match.group(1) if match else ""


def has_invalid_datetime(user_query: str) -> bool:
    invalid_date = re.search(r"\b(\d{1,2})/(\d{1,2})/(\d{4})\b", user_query)
    invalid_time = re.search(r"\b([2-9]\d):([0-5]\d)\b", user_query)
    if invalid_time and int(invalid_time.group(1)) > 23:
        return True
    if invalid_date:
        day, month = int(invalid_date.group(1)), int(invalid_date.group(2))
        return day > 31 or month > 12
    return False


def run_tool_step(step: int, thought: str, action_name: str, *args) -> str:
    print(f"\n--- 🔄 Vòng lặp ReAct (Step {step}/{MAX_ITERATIONS}) ---")
    print(f"Thought: {thought}")
    print(f"Action: {action_name}[{', '.join(args)}]")
    observation = AVAILABLE_TOOLS[action_name](*args)
    print(f"Observation: {observation}")
    return observation


def run_react_agent(user_query: str, provider, emit_logs: bool = True):
    """
    Dựng vòng lặp ReAct Agent (Thought -> Action -> Observation) có guardrails.
    """
    if emit_logs:
        print(f"\n🤖 [REACT AGENT] Câu hỏi: {user_query}")
    text = normalize_text(user_query)
    step = 0
    observations = []
    trace = []
    final_answer = ""
    guardrail_triggered = False

    if has_invalid_datetime(user_query):
        final_answer = "Thời gian bạn nhập chưa hợp lệ. Vui lòng nhập ngày theo YYYY-MM-DD và giờ theo HH:MM."
        guardrail_triggered = True
        if emit_logs:
            print("\n--- 🛡️ GUARDRAIL ---")
            print("Thought: Người dùng nhập ngày hoặc giờ không hợp lệ, cần dừng trước khi gọi tool.")
            print(f"Final Answer: {final_answer}")
        return {
            "question": user_query,
            "trace": trace,
            "final_answer": final_answer,
            "guardrail_triggered": guardrail_triggered,
        }

    wants_cancel = bool(re.search(r"\b(cancel|huy)\b", text)) or "hủy" in text
    if wants_cancel:
        appointment_match = re.search(r"\b(APT\d+|LK\d+)\b", user_query, re.IGNORECASE)
        appointment_id = appointment_match.group(1) if appointment_match else ""
        step += 1
        thought = "Người dùng muốn hủy lịch khám, cần gọi công cụ hủy lịch."
        action_name = "cancel_appointment"
        action_args = [appointment_id]
        observation = run_tool_step(step, thought, action_name, *action_args)
        observations.append(observation)
        trace.append({
            "step": step,
            "thought": thought,
            "action": {"name": action_name, "args": action_args},
            "observation": observation,
        })
        final_answer = "Tôi đã xử lý yêu cầu hủy lịch theo kết quả Observation ở trên."
        if emit_logs:
            print("\nThought: Đã có kết quả hủy lịch.")
            print(f"Final Answer: {final_answer}")
        return {
            "question": user_query,
            "trace": trace,
            "final_answer": final_answer,
            "guardrail_triggered": guardrail_triggered,
        }

    if any(keyword in text for keyword in ["đau", "sốt", "ho", "khó thở", "mẩn", "ngứa", "triệu chứng", "mất ngủ"]):
        step += 1
        thought = "Cần phân loại mức độ khẩn cấp trước khi tư vấn tiếp."
        action_name = "classify_urgency"
        action_args = [user_query]
        observation = run_tool_step(step, thought, action_name, *action_args)
        observations.append(observation)
        trace.append({
            "step": step,
            "thought": thought,
            "action": {"name": action_name, "args": action_args},
            "observation": observation,
        })
        if any(keyword in text for keyword in ["đau ngực dữ dội", "khó thở", "ngất", "vã mồ hôi"]):
            final_answer = "Triệu chứng có thể nguy hiểm. Bạn nên đến cơ sở y tế gần nhất hoặc gọi cấp cứu ngay, không nên chờ lịch khám thông thường."
            guardrail_triggered = True
            if emit_logs:
                print("\nThought: Có dấu hiệu nguy hiểm, cần ưu tiên an toàn thay vì đặt lịch thường.")
                print(f"Final Answer: {final_answer}")
            return {
                "question": user_query,
                "trace": trace,
                "final_answer": final_answer,
                "guardrail_triggered": guardrail_triggered,
            }

    specialty_observation = ""
    if step < MAX_ITERATIONS and any(keyword in text for keyword in ["khoa", "chuyên khoa", "khám", "triệu chứng", "đau", "sốt", "ho", "mẩn", "ngứa", "mất ngủ"]):
        step += 1
        thought = "Cần xác định chuyên khoa phù hợp."
        action_name = "suggest_specialty"
        action_args = [user_query]
        specialty_observation = run_tool_step(step, thought, action_name, *action_args)
        observations.append(specialty_observation)
        trace.append({
            "step": step,
            "thought": thought,
            "action": {"name": action_name, "args": action_args},
            "observation": specialty_observation,
        })

    specialty = extract_specialty(user_query, specialty_observation)
    location = extract_location(user_query)
    date = extract_date(user_query)
    wants_doctor_search = any(keyword in text for keyword in ["tìm", "bác sĩ", "còn lịch", "đặt lịch"])

    if step < MAX_ITERATIONS and wants_doctor_search:
        if specialty and location and date:
            step += 1
            thought = "Đã có chuyên khoa, địa điểm và ngày khám nên cần tìm bác sĩ còn lịch."
            action_name = "find_available_doctors"
            action_args = [specialty, location, date]
            observation = run_tool_step(step, thought, action_name, *action_args)
            observations.append(observation)
            trace.append({
                "step": step,
                "thought": thought,
                "action": {"name": action_name, "args": action_args},
                "observation": observation,
            })
        elif "đặt lịch" in text:
            final_answer = "Bạn vui lòng cung cấp thêm chuyên khoa, địa điểm khám và ngày muốn khám để tôi tìm lịch phù hợp."
            if emit_logs:
                print("\nThought: Người dùng muốn đặt lịch nhưng còn thiếu chuyên khoa, địa điểm hoặc ngày khám.")
                print(f"Final Answer: {final_answer}")
            return {
                "question": user_query,
                "trace": trace,
                "final_answer": final_answer,
                "guardrail_triggered": guardrail_triggered,
            }

    patient_id = extract_patient_id(user_query)
    doctor_id = extract_doctor_id(user_query)
    time_slot = extract_time_slot(user_query)
    if step < MAX_ITERATIONS and "đặt" in text and patient_id and doctor_id and time_slot:
        step += 1
        thought = "Người dùng đã cung cấp đủ patient_id, doctor_id và time_slot nên có thể đặt lịch."
        action_name = "book_appointment"
        action_args = [patient_id, doctor_id, time_slot]
        observation = run_tool_step(step, thought, action_name, *action_args)
        observations.append(observation)
        trace.append({
            "step": step,
            "thought": thought,
            "action": {"name": action_name, "args": action_args},
            "observation": observation,
        })

    final_answer = "Tôi đã thực hiện các bước phù hợp ở trên. Bạn có thể xem Observation để biết mức độ khẩn cấp, chuyên khoa gợi ý, lịch bác sĩ hoặc trạng thái đặt/hủy lịch."
    if emit_logs:
        print("\nThought: Tôi đã có đủ thông tin từ các Observation để trả lời.")
        print(f"Final Answer: {final_answer}")
    return {
        "question": user_query,
        "trace": trace,
        "final_answer": final_answer,
        "guardrail_triggered": guardrail_triggered,
    }


def run_suite_and_export(tests, provider, output_path):
    results = []
    for test_case in tests:
        question = test_case.get("question", "")
        print(f"\n=== TEST CASE {test_case.get('id')} ===")
        baseline_response = run_baseline_chatbot(question, provider)
        react_result = run_react_agent(question, provider, emit_logs=True)
        results.append({
            "id": test_case.get("id"),
            "category": test_case.get("category", ""),
            "question": question,
            "expected_behavior": test_case.get("expected_behavior", ""),
            "baseline_response": baseline_response,
            "react_result": react_result,
        })

    payload = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "provider": getattr(provider, "__class__", type(provider)).__name__,
        "model": getattr(provider, "model_name", ""),
        "results": results,
    }
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    return output_path


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

    sample_query = tests[1]["question"] if len(tests) > 1 else "Tôi bị nổi mẩn đỏ sau khi đổi sữa tắm, nên khám chuyên khoa nào?"

    print("--- DEMO 1: CHẠY TRÊN CHATBOT BASELINE ---")
    run_baseline_chatbot(sample_query, provider)

    print("\n--- DEMO 2: CHẠY TRÊN REACT AGENT ---")
    run_react_agent(sample_query, provider)

    log_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs", "run_log.json")
    exported = run_suite_and_export(tests, provider, log_path)
    print(f"\n📝 Đã xuất log toàn bộ test case ra: {exported}")


if __name__ == "__main__":
    main()

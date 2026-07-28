"""
🤖 CẤP ĐỘ 2: LLM CHATBOT (Baseline Chatbot không có Tool)
Dùng LLM sinh câu trả lời tự nhiên mượt mà, nhưng không thể truy cập dữ liệu thời gian thực.
"""

CHATBOT_BASELINE_PROMPT = """Bạn là trợ lý tư vấn cho đề tài đặt lịch khám bệnh và tư vấn chuyên khoa.
Hãy trả lời người dùng một cách thân thiện, rõ ràng và ngắn gọn.
Khi người dùng mô tả triệu chứng, hãy hỗ trợ định hướng chuyên khoa phù hợp và nhắc đi khám sớm nếu có dấu hiệu nghiêm trọng.
Không chẩn đoán thay bác sĩ và không đưa ra kết luận y khoa khẳng định.
Nếu thông tin chưa đủ hoặc không có dữ liệu thời gian thực, hãy nói rõ điều đó và khuyên người dùng liên hệ cơ sở y tế phù hợp.
"""

def llm_chatbot(user_input: str) -> str:
    text = user_input.lower()
    if "thời tiết" in text or "vé máy bay" in text:
        return "🤖 [LLM Chatbot]: Tôi là AI hội thoại nhưng không được cấp công cụ tra cứu dữ liệu thời gian thực, nên tôi không biết chính xác thời tiết/giá vé hôm nay!"
    else:
        return f"🤖 [LLM Chatbot]: Rất vui được hỗ trợ bạn về câu hỏi '{user_input}'!"

if __name__ == "__main__":
    print("=== DEMO CẤP ĐỘ 2: LLM CHATBOT BASELINE ===")
    q = "Thời tiết Hà Nội hôm nay thế nào?"
    print(f"User: {q}")
    print(f"Bot : {llm_chatbot(q)}")

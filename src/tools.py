"""
🛠️ TOOL REGISTRY & SCHEMAS (Dành cho Role 2: Tool & Spec Engineer)
Chủ đề: Đặt Lịch Khám Bệnh & Tư Vấn Chuyên Khoa

Nơi khai báo tất cả các "món đồ nghề" mà ReAct Agent có thể gọi.
Mỗi hàm trả về chuỗi (str) mô tả kết quả hoặc thông báo lỗi rõ ràng,
KHÔNG raise Exception để tránh crash chương trình (Guardrail-safe).

Danh sách Tools:
    1. classify_urgency(symptoms)        - Phân loại mức độ khẩn cấp
    2. suggest_specialty(symptoms)        - Gợi ý chuyên khoa phù hợp
    3. find_available_doctors(specialty, location, date) - Tìm bác sĩ còn lịch
    4. book_appointment(patient_id, doctor_id, time_slot) - Đặt lịch khám
    5. cancel_appointment(appointment_id) - Hủy lịch khám
"""


# ============================================================
# 📦 DỮ LIỆU GIẢ LẬP (Mock Database)
# ============================================================

# Từ khóa triệu chứng → mức độ khẩn cấp
URGENCY_KEYWORDS = {
    "khám sớm": {
        "keywords": [
            "sốt cao", "đau đầu dữ dội", "nôn liên tục", "tiêu chảy nhiều",
            "đau bụng kéo dài", "ho ra máu", "sưng tấy", "nhiễm trùng",
            "sốt kéo dài", "khó nuốt", "đau lưng dữ dội", "chóng mặt liên tục",
            "phát ban toàn thân", "mắt đỏ sưng"
        ],
        "level": "🟡 CẦN KHÁM SỚM (trong 24h)",
        "advice": "Bạn nên đặt lịch khám trong vòng 24 giờ tới để được chẩn đoán kịp thời."
    },
    "thường": {
        "keywords": [
            "ho nhẹ", "sổ mũi", "đau họng", "mệt mỏi", "nhức đầu nhẹ",
            "đau lưng", "mất ngủ", "dị ứng", "ngứa", "chàm", "mụn",
            "đau răng", "đau khớp", "cận thị", "viễn thị", "táo bón",
            "đầy bụng", "ợ chua", "đau vai gáy", "tê tay chân"
        ],
        "level": "🟢 CÓ THỂ ĐẶT LỊCH THƯỜNG",
        "advice": "Bạn có thể đặt lịch khám trong tuần này, không cần quá gấp."
    }
}

# Từ khóa triệu chứng → chuyên khoa
SPECIALTY_MAP = {
    "Tim mạch": [
        "đau ngực", "hồi hộp", "tức ngực", "khó thở", "tim đập nhanh",
        "huyết áp cao", "huyết áp thấp", "đau tim", "phù chân"
    ],
    "Da liễu": [
        "ngứa", "phát ban", "mụn", "chàm", "nổi mề đay", "dị ứng da",
        "nấm da", "vẩy nến", "rụng tóc", "da khô"
    ],
    "Tai Mũi Họng": [
        "đau họng", "viêm họng", "sổ mũi", "nghẹt mũi",
        "ù tai", "đau tai", "viêm xoang", "khàn tiếng", "amidan"
    ],
    "Tiêu hóa": [
        "đau bụng", "tiêu chảy", "táo bón", "đầy bụng", "ợ chua",
        "buồn nôn", "nôn", "đau dạ dày", "trào ngược", "khó tiêu"
    ],
    "Thần kinh": [
        "đau đầu", "nhức đầu", "chóng mặt", "mất ngủ", "tê tay chân",
        "co giật", "run tay", "đau dây thần kinh", "mất trí nhớ"
    ],
    "Cơ xương khớp": [
        "đau lưng", "đau khớp", "đau vai gáy", "cứng khớp", "thoát vị đĩa đệm",
        "gãy xương", "bong gân", "viêm khớp", "đau cơ"
    ],
    "Mắt": [
        "đau mắt", "mờ mắt", "cận thị", "viễn thị", "mắt đỏ",
        "chảy nước mắt", "nhức mắt", "loạn thị"
    ],
    "Nhi khoa": [
        "trẻ sốt", "trẻ ho", "trẻ tiêu chảy", "trẻ biếng ăn",
        "trẻ quấy khóc", "trẻ phát ban", "sốt ở trẻ em"
    ],
    "Sản phụ khoa": [
        "đau bụng kinh", "rối loạn kinh nguyệt", "mang thai",
        "thai kỳ", "siêu âm thai", "đau vùng chậu"
    ],
    "Răng Hàm Mặt": [
        "đau răng", "sâu răng", "chảy máu nướu", "viêm nướu",
        "nhổ răng", "niềng răng", "đau hàm"
    ]
}

# Dữ liệu bác sĩ giả lập
MOCK_DOCTORS = [
    {
        "id": "BS001", "name": "PGS.TS. Nguyễn Văn An",
        "specialty": "Tim mạch", "hospital": "Bệnh viện Bạch Mai",
        "location": "Hà Nội",
        "schedule": {
            "2026-07-29": ["08:00", "09:00", "10:00", "14:00"],
            "2026-07-30": ["08:00", "09:30", "15:00"],
            "2026-07-31": ["10:00", "14:00", "16:00"]
        },
        "fee": "500,000 VNĐ"
    },
    {
        "id": "BS002", "name": "TS.BS. Trần Thị Bình",
        "specialty": "Tim mạch", "hospital": "Bệnh viện Chợ Rẫy",
        "location": "TP.HCM",
        "schedule": {
            "2026-07-29": ["09:00", "10:30", "14:00"],
            "2026-07-30": ["08:00", "11:00"],
            "2026-07-31": ["08:30", "10:00", "14:30"]
        },
        "fee": "450,000 VNĐ"
    },
    {
        "id": "BS003", "name": "BS.CKI. Lê Minh Châu",
        "specialty": "Da liễu", "hospital": "Bệnh viện Da liễu TW",
        "location": "Hà Nội",
        "schedule": {
            "2026-07-29": ["08:00", "09:00", "10:00"],
            "2026-07-30": ["14:00", "15:00"],
            "2026-07-31": ["08:00", "09:00"]
        },
        "fee": "350,000 VNĐ"
    },
    {
        "id": "BS004", "name": "ThS.BS. Phạm Đức Dũng",
        "specialty": "Tai Mũi Họng", "hospital": "Bệnh viện Tai Mũi Họng TW",
        "location": "Hà Nội",
        "schedule": {
            "2026-07-29": ["08:30", "10:00", "14:00", "15:30"],
            "2026-07-30": ["09:00", "11:00", "14:00"],
            "2026-07-31": ["08:00", "10:30"]
        },
        "fee": "400,000 VNĐ"
    },
    {
        "id": "BS005", "name": "PGS.TS. Hoàng Thị Êm",
        "specialty": "Tiêu hóa", "hospital": "Bệnh viện 108",
        "location": "Hà Nội",
        "schedule": {
            "2026-07-29": ["08:00", "09:30", "14:00"],
            "2026-07-30": ["10:00", "14:00", "16:00"],
            "2026-07-31": ["08:00", "09:00", "11:00"]
        },
        "fee": "500,000 VNĐ"
    },
    {
        "id": "BS006", "name": "TS.BS. Vũ Quốc Phong",
        "specialty": "Thần kinh", "hospital": "Bệnh viện Nhân dân 115",
        "location": "TP.HCM",
        "schedule": {
            "2026-07-29": ["08:00", "10:00", "14:00"],
            "2026-07-30": ["09:00", "11:00"],
            "2026-07-31": ["08:00", "14:00", "15:00"]
        },
        "fee": "550,000 VNĐ"
    },
    {
        "id": "BS007", "name": "BS.CKII. Đỗ Thị Giang",
        "specialty": "Cơ xương khớp", "hospital": "Bệnh viện Việt Đức",
        "location": "Hà Nội",
        "schedule": {
            "2026-07-29": ["09:00", "10:30", "14:00"],
            "2026-07-30": ["08:00", "10:00", "15:00"],
            "2026-07-31": ["09:00", "11:00"]
        },
        "fee": "400,000 VNĐ"
    },
    {
        "id": "BS008", "name": "ThS.BS. Ngô Văn Hải",
        "specialty": "Mắt", "hospital": "Bệnh viện Mắt TW",
        "location": "Hà Nội",
        "schedule": {
            "2026-07-29": ["08:00", "09:00", "14:00", "15:00"],
            "2026-07-30": ["10:00", "14:00"],
            "2026-07-31": ["08:00", "09:30", "11:00"]
        },
        "fee": "350,000 VNĐ"
    },
    {
        "id": "BS009", "name": "BS.CKI. Mai Thị Kim",
        "specialty": "Nhi khoa", "hospital": "Bệnh viện Nhi TW",
        "location": "Hà Nội",
        "schedule": {
            "2026-07-29": ["08:00", "09:00", "10:00", "14:00", "15:00"],
            "2026-07-30": ["08:00", "09:00", "14:00"],
            "2026-07-31": ["08:00", "10:00", "14:00"]
        },
        "fee": "400,000 VNĐ"
    },
    {
        "id": "BS010", "name": "PGS.TS. Lý Thị Lan",
        "specialty": "Sản phụ khoa", "hospital": "Bệnh viện Từ Dũ",
        "location": "TP.HCM",
        "schedule": {
            "2026-07-29": ["08:00", "09:30", "14:00"],
            "2026-07-30": ["08:00", "10:00", "14:00", "16:00"],
            "2026-07-31": ["09:00", "11:00", "14:00"]
        },
        "fee": "500,000 VNĐ"
    },
    {
        "id": "BS011", "name": "TS.BS. Trương Văn Minh",
        "specialty": "Tiêu hóa", "hospital": "Bệnh viện Đại học Y Dược TP.HCM",
        "location": "TP.HCM",
        "schedule": {
            "2026-07-29": ["09:00", "10:00", "14:30"],
            "2026-07-30": ["08:00", "14:00"],
            "2026-07-31": ["08:00", "10:00", "15:00"]
        },
        "fee": "480,000 VNĐ"
    },
    {
        "id": "BS012", "name": "BS.CKII. Phan Thị Ngọc",
        "specialty": "Răng Hàm Mặt", "hospital": "Bệnh viện RHM TW",
        "location": "Hà Nội",
        "schedule": {
            "2026-07-29": ["08:00", "10:00", "14:00"],
            "2026-07-30": ["09:00", "14:00", "16:00"],
            "2026-07-31": ["08:00", "10:00"]
        },
        "fee": "300,000 VNĐ"
    }
]

# Lịch khám đã đặt (Mock in-memory database)
BOOKED_APPOINTMENTS = {}
_appointment_counter = 0


# ============================================================
# 🔧 TOOL 1: classify_urgency
# ============================================================

def classify_urgency(symptoms: str) -> str:
    """
    Phân loại mức độ khẩn cấp từ triệu chứng của bệnh nhân.

    Dựa trên triệu chứng mô tả, hàm sẽ phân loại vào 1 trong 2 mức:
    - 🟡 CẦN KHÁM SỚM: Triệu chứng nghiêm trọng, cần khám trong vòng 24 giờ.
    - 🟢 ĐẶT LỊCH THƯỜNG: Triệu chứng nhẹ, có thể đặt lịch khám bình thường.

    Args:
        symptoms (str): Mô tả triệu chứng của bệnh nhân
                        (Ví dụ: 'đau ngực, khó thở', 'ho nhẹ, sổ mũi')

    Returns:
        str: Kết quả phân loại bao gồm mức độ khẩn cấp và lời khuyên hành động.
    """
    try:
        if not symptoms or not str(symptoms).strip():
            return "LỖI: Vui lòng mô tả triệu chứng để phân loại mức độ khẩn cấp."

        symptoms = str(symptoms)
        symptoms_lower = symptoms.lower().strip()

        # Kiểm tra theo thứ tự ưu tiên: khám sớm → thường
        for level_key in ["khám sớm", "thường"]:
            level_data = URGENCY_KEYWORDS[level_key]
            matched = [kw for kw in level_data["keywords"] if kw in symptoms_lower]
            if matched:
                result = (
                    f"📋 KẾT QUẢ PHÂN LOẠI KHẨN CẤP:\n"
                    f"   Triệu chứng: {symptoms}\n"
                    f"   Từ khóa phát hiện: {', '.join(matched)}\n"
                    f"   Mức độ: {level_data['level']}\n"
                    f"   💡 Lời khuyên: {level_data['advice']}"
                )
                return result

        # Không khớp từ khóa nào → mặc định đặt lịch thường
        return (
            f"📋 KẾT QUẢ PHÂN LOẠI KHẨN CẤP:\n"
            f"   Triệu chứng: {symptoms}\n"
            f"   Mức độ: 🟢 CÓ THỂ ĐẶT LỊCH THƯỜNG\n"
            f"   💡 Lời khuyên: Triệu chứng chưa rõ ràng. Bạn nên đặt lịch khám "
            f"để được bác sĩ tư vấn chi tiết hơn."
        )
    except Exception as e:
        return f"LỖI: Đã xảy ra lỗi khi phân loại triệu chứng: {e}"


# ============================================================
# 🔧 TOOL 2: suggest_specialty
# ============================================================

def suggest_specialty(symptoms: str) -> str:
    """
    Gợi ý chuyên khoa phù hợp dựa trên triệu chứng của bệnh nhân.

    Phân tích triệu chứng và đối chiếu với bảng chuyên khoa để gợi ý
    khoa khám phù hợp nhất. Có thể gợi ý nhiều chuyên khoa nếu triệu
    chứng liên quan đến nhiều lĩnh vực.

    Args:
        symptoms (str): Mô tả triệu chứng của bệnh nhân
                        (Ví dụ: 'đau đầu, chóng mặt', 'ngứa, phát ban')

    Returns:
        str: Danh sách chuyên khoa được gợi ý kèm lý do, hoặc thông báo lỗi.
    """
    try:
        if not symptoms or not str(symptoms).strip():
            return "LỖI: Vui lòng mô tả triệu chứng để gợi ý chuyên khoa phù hợp."

        symptoms = str(symptoms)
        symptoms_lower = symptoms.lower().strip()
        suggestions = []

        for specialty, keywords in SPECIALTY_MAP.items():
            matched = [kw for kw in keywords if kw in symptoms_lower]
            if matched:
                suggestions.append({
                    "specialty": specialty,
                    "matched_keywords": matched
                })

        if not suggestions:
            return (
                f"🏥 GỢI Ý CHUYÊN KHOA:\n"
                f"   Triệu chứng: {symptoms}\n"
                f"   Kết quả: Không tìm thấy chuyên khoa phù hợp từ triệu chứng mô tả.\n"
                f"   💡 Gợi ý: Bạn nên đặt lịch khám tại khoa Nội tổng quát "
                f"để được bác sĩ thăm khám và chuyển chuyên khoa phù hợp."
            )

        result_lines = [
            f"🏥 GỢI Ý CHUYÊN KHOA:",
            f"   Triệu chứng: {symptoms}",
            f"   Số chuyên khoa phù hợp: {len(suggestions)}",
            ""
        ]

        for i, sug in enumerate(suggestions, 1):
            result_lines.append(
                f"   {i}. Khoa {sug['specialty']} "
                f"(dựa trên: {', '.join(sug['matched_keywords'])})"
            )

        if len(suggestions) > 1:
            result_lines.append(
                f"\n   💡 Gợi ý: Nên ưu tiên khám khoa {suggestions[0]['specialty']} trước."
            )

        return "\n".join(result_lines)
    except Exception as e:
        return f"LỖI: Đã xảy ra lỗi khi gợi ý chuyên khoa: {e}"


# ============================================================
# 🔧 TOOL 3: find_available_doctors
# ============================================================

def find_available_doctors(specialty: str, location: str, date: str) -> str:
    """
    Tìm danh sách bác sĩ còn lịch trống theo chuyên khoa, địa điểm và ngày khám.

    Tìm kiếm trong cơ sở dữ liệu bác sĩ và trả về danh sách các bác sĩ
    phù hợp với tiêu chí tìm kiếm, bao gồm các khung giờ còn trống.

    Args:
        specialty (str): Tên chuyên khoa cần tìm
                         (Ví dụ: 'Tim mạch', 'Da liễu', 'Tai Mũi Họng')
        location (str):  Thành phố/khu vực
                         (Ví dụ: 'Hà Nội', 'TP.HCM')
        date (str):      Ngày khám theo định dạng YYYY-MM-DD
                         (Ví dụ: '2026-07-29')

    Returns:
        str: Danh sách bác sĩ khả dụng kèm thông tin chi tiết, hoặc thông báo lỗi.
    """
    try:
        # Kiểm tra tham số đầu vào
        if not specialty or not str(specialty).strip():
            return "LỖI: Vui lòng cung cấp tên chuyên khoa cần tìm (VD: 'Tim mạch', 'Da liễu')."

        if not location or not str(location).strip():
            return "LỖI: Vui lòng cung cấp địa điểm muốn khám (VD: 'Hà Nội', 'TP.HCM')."

        if not date or not str(date).strip():
            return "LỖI: Vui lòng cung cấp ngày muốn khám theo định dạng YYYY-MM-DD."

        # Chuẩn hóa tham số
        specialty = str(specialty)
        location = str(location)
        date = str(date)
        specialty_lower = specialty.lower().strip()
        location_lower = location.lower().strip()

        # Validate định dạng ngày cơ bản
        date = date.strip()
        parts = date.split("-")
        if len(parts) != 3 or not all(p.isdigit() for p in parts):
            return (
                f"LỖI: Ngày '{date}' không đúng định dạng. "
                f"Vui lòng nhập theo định dạng YYYY-MM-DD (VD: '2026-07-29')."
            )

        year, month, day = int(parts[0]), int(parts[1]), int(parts[2])
        if month < 1 or month > 12:
            return f"LỖI: Tháng '{month}' không hợp lệ. Tháng phải từ 1 đến 12."
        if day < 1 or day > 31:
            return f"LỖI: Ngày '{day}' không hợp lệ. Ngày phải từ 1 đến 31."

        # Tìm bác sĩ phù hợp
        found_doctors = []
        for doc in MOCK_DOCTORS:
            spec_match = doc["specialty"].lower() == specialty_lower
            loc_match = (
                location_lower in doc["location"].lower()
                or doc["location"].lower() in location_lower
            )
            if spec_match and loc_match:
                slots = doc["schedule"].get(date, [])
                if slots:
                    found_doctors.append({
                        "doctor": doc,
                        "available_slots": slots
                    })

        if not found_doctors:
            return (
                f"🔍 KẾT QUẢ TÌM BÁC SĨ:\n"
                f"   Chuyên khoa: {specialty} | Khu vực: {location} | Ngày: {date}\n"
                f"   ❌ Không tìm thấy bác sĩ nào phù hợp.\n"
                f"   💡 Gợi ý: Hãy thử tìm ở ngày khác hoặc khu vực lân cận."
            )

        result_lines = [
            f"🔍 KẾT QUẢ TÌM BÁC SĨ:",
            f"   Chuyên khoa: {specialty} | Khu vực: {location} | Ngày: {date}",
            f"   ✅ Tìm thấy {len(found_doctors)} bác sĩ phù hợp:",
            ""
        ]

        for i, item in enumerate(found_doctors, 1):
            doc = item["doctor"]
            slots = item["available_slots"]
            result_lines.extend([
                f"   {i}. {doc['name']} (Mã BS: {doc['id']})",
                f"      🏥 {doc['hospital']} - {doc['location']}",
                f"      🕐 Khung giờ trống: {', '.join(slots)}",
                f"      💰 Phí khám: {doc['fee']}",
                ""
            ])

        return "\n".join(result_lines)
    except Exception as e:
        return f"LỖI: Đã xảy ra lỗi khi tìm bác sĩ: {e}"


# ============================================================
# 🔧 TOOL 4: book_appointment
# ============================================================

def book_appointment(patient_id: str, doctor_id: str, time_slot: str) -> str:
    """
    Đặt một lịch khám cụ thể cho bệnh nhân với bác sĩ và khung giờ đã chọn.

    Kiểm tra tính hợp lệ của bác sĩ, khung giờ, và trạng thái trùng lịch
    trước khi xác nhận đặt lịch thành công.

    Args:
        patient_id (str): Mã định danh bệnh nhân
                          (Ví dụ: 'BN001', 'BN_NguyenVanA')
        doctor_id (str):  Mã định danh bác sĩ
                          (Ví dụ: 'BS001', 'BS005')
        time_slot (str):  Khung giờ muốn đặt, định dạng 'YYYY-MM-DD HH:MM'
                          (Ví dụ: '2026-07-29 08:00')

    Returns:
        str: Thông tin xác nhận đặt lịch thành công, hoặc thông báo lỗi chi tiết.
    """
    global _appointment_counter

    try:
        # Kiểm tra tham số đầu vào
        if not patient_id or not str(patient_id).strip():
            return "LỖI: Vui lòng cung cấp mã bệnh nhân (VD: 'BN001')."

        if not doctor_id or not str(doctor_id).strip():
            return "LỖI: Vui lòng cung cấp mã bác sĩ (VD: 'BS001')."

        if not time_slot or not str(time_slot).strip():
            return (
                "LỖI: Vui lòng cung cấp khung giờ đặt lịch "
                "theo định dạng 'YYYY-MM-DD HH:MM' (VD: '2026-07-29 08:00')."
            )

        patient_id = str(patient_id).strip()
        doctor_id = str(doctor_id).strip().upper()
        time_slot = str(time_slot).strip()

        # Tìm bác sĩ theo ID
        target_doctor = None
        for doc in MOCK_DOCTORS:
            if doc["id"] == doctor_id:
                target_doctor = doc
                break

        if not target_doctor:
            return (
                f"LỖI: Không tìm thấy bác sĩ với mã '{doctor_id}'. "
                f"Vui lòng kiểm tra lại mã bác sĩ."
            )

        # Phân tích time_slot → ngày + giờ
        slot_parts = time_slot.split(" ")
        if len(slot_parts) != 2:
            return (
                f"LỖI: Khung giờ '{time_slot}' không đúng định dạng. "
                f"Vui lòng nhập 'YYYY-MM-DD HH:MM' (VD: '2026-07-29 08:00')."
            )

        date_part, time_part = slot_parts[0], slot_parts[1]

        # Kiểm tra ngày có trong lịch bác sĩ không
        if date_part not in target_doctor["schedule"]:
            return (
                f"LỖI: Bác sĩ {target_doctor['name']} không có lịch khám ngày {date_part}.\n"
                f"   Các ngày có lịch: {', '.join(target_doctor['schedule'].keys())}"
            )

        # Kiểm tra khung giờ có trống không
        available_slots = target_doctor["schedule"][date_part]
        if time_part not in available_slots:
            return (
                f"LỖI: Khung giờ {time_part} ngày {date_part} đã được đặt "
                f"hoặc không có trong lịch bác sĩ {target_doctor['name']}.\n"
                f"   Các khung giờ trống ngày {date_part}: {', '.join(available_slots)}"
            )

        # Kiểm tra bệnh nhân đã có lịch trùng chưa
        for appt_id, appt in BOOKED_APPOINTMENTS.items():
            if appt["patient_id"] == patient_id and appt["time_slot"] == time_slot:
                return (
                    f"LỖI: Bệnh nhân {patient_id} đã có lịch khám vào {time_slot} "
                    f"(Mã lịch: {appt_id}). Không thể đặt trùng."
                )

        # Đặt lịch thành công
        _appointment_counter += 1
        appointment_id = f"LK{_appointment_counter:04d}"

        BOOKED_APPOINTMENTS[appointment_id] = {
            "patient_id": patient_id,
            "doctor_id": doctor_id,
            "doctor_name": target_doctor["name"],
            "specialty": target_doctor["specialty"],
            "hospital": target_doctor["hospital"],
            "time_slot": time_slot,
            "status": "confirmed"
        }

        # Xóa khung giờ khỏi danh sách trống
        target_doctor["schedule"][date_part].remove(time_part)

        return (
            f"✅ ĐẶT LỊCH KHÁM THÀNH CÔNG!\n"
            f"   📌 Mã lịch hẹn: {appointment_id}\n"
            f"   👤 Bệnh nhân: {patient_id}\n"
            f"   👨‍⚕️ Bác sĩ: {target_doctor['name']} ({doctor_id})\n"
            f"   🏥 Bệnh viện: {target_doctor['hospital']}\n"
            f"   📅 Khoa: {target_doctor['specialty']}\n"
            f"   🕐 Thời gian: {time_slot}\n"
            f"   💰 Phí khám: {target_doctor['fee']}\n"
            f"   ⚠️ Lưu ý: Vui lòng đến trước giờ hẹn 15 phút để làm thủ tục."
        )
    except Exception as e:
        return f"LỖI: Đã xảy ra lỗi khi đặt lịch khám: {e}"


# ============================================================
# 🔧 TOOL 5: cancel_appointment
# ============================================================

def cancel_appointment(appointment_id: str) -> str:
    """
    Hủy một lịch khám đã đặt theo mã lịch hẹn.

    Kiểm tra mã lịch hẹn có tồn tại và chưa bị hủy trước đó,
    sau đó cập nhật trạng thái và hoàn trả khung giờ vào lịch trống.

    Args:
        appointment_id (str): Mã lịch hẹn cần hủy
                              (Ví dụ: 'LK0001', 'LK0002')

    Returns:
        str: Thông tin xác nhận hủy lịch thành công, hoặc thông báo lỗi chi tiết.
    """
    try:
        if not appointment_id or not str(appointment_id).strip():
            return "LỖI: Vui lòng cung cấp mã lịch hẹn cần hủy (VD: 'LK0001')."

        appointment_id = str(appointment_id).strip().upper()

        # Tìm lịch hẹn
        if appointment_id not in BOOKED_APPOINTMENTS:
            return (
                f"LỖI: Không tìm thấy lịch hẹn với mã '{appointment_id}'. "
                f"Vui lòng kiểm tra lại mã lịch hẹn."
            )

        appt = BOOKED_APPOINTMENTS[appointment_id]

        # Kiểm tra đã hủy trước đó chưa
        if appt["status"] == "cancelled":
            return (
                f"LỖI: Lịch hẹn {appointment_id} đã được hủy trước đó. "
                f"Không cần hủy lại."
            )

        # Hoàn trả khung giờ vào lịch bác sĩ
        time_slot = appt["time_slot"]
        slot_parts = time_slot.split(" ")
        if len(slot_parts) == 2:
            date_part, time_part = slot_parts[0], slot_parts[1]
            for doc in MOCK_DOCTORS:
                if doc["id"] == appt["doctor_id"]:
                    if date_part in doc["schedule"]:
                        doc["schedule"][date_part].append(time_part)
                        doc["schedule"][date_part].sort()
                    break

        # Cập nhật trạng thái
        appt["status"] = "cancelled"

        return (
            f"🗑️ HỦY LỊCH KHÁM THÀNH CÔNG!\n"
            f"   📌 Mã lịch hẹn: {appointment_id}\n"
            f"   👤 Bệnh nhân: {appt['patient_id']}\n"
            f"   👨‍⚕️ Bác sĩ: {appt['doctor_name']} ({appt['doctor_id']})\n"
            f"   🏥 Bệnh viện: {appt['hospital']}\n"
            f"   📅 Khoa: {appt['specialty']}\n"
            f"   🕐 Thời gian đã hủy: {appt['time_slot']}\n"
            f"   ✅ Khung giờ đã được hoàn trả vào lịch trống của bác sĩ."
        )
    except Exception as e:
        return f"LỖI: Đã xảy ra lỗi khi hủy lịch hẹn: {e}"


# ============================================================
# 📋 DANH SÁCH CÁC TOOL ĐĂNG KÝ CHO AGENT SỬ DỤNG
# ============================================================

AVAILABLE_TOOLS = {
    "classify_urgency": classify_urgency,
    "suggest_specialty": suggest_specialty,
    "find_available_doctors": find_available_doctors,
    "book_appointment": book_appointment,
    "cancel_appointment": cancel_appointment,
}

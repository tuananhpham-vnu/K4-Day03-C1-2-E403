# Failure Modes cua cac Tool

De tai: Dat Lich Kham Benh & Tu Van Chuyen Khoa

## 1. `classify_urgency(symptoms)`

- **Thieu thong tin ngu canh:** Trieu chung qua chung chung, vi du: "toi thay met", "dau", khien he thong kho phan loai dung muc do nghiem trong.
- **Nhieu du lieu:** Nguoi dung nhap noi dung khong lien quan y te nhu chitchat, troll, spam, khien tool co the loi hoac phan loai sai.
- **Bo sot dau hieu nguy hiem:** Tool khong nhan dien duoc cac trieu chung cap cuu nhu dau nguc du doi, kho tho, ngat, meo mieng.

## 2. `suggest_specialty(symptoms)`

- **Trieu chung da khoa:** Mot trieu chung co the lien quan nhieu chuyen khoa, vi du dau nguc co the thuoc Tim mach, Ho hap hoac Tieu hoa.
- **Tu vung dia phuong/sai chinh ta:** Nguoi dung dung tu long, viet sai chinh ta hoac mo ta khong theo thuat ngu y khoa khien tool nhan dien sai.
- **Thieu thong tin bo sung:** Khong co tuoi, gioi tinh, benh nen hoac thoi gian xuat hien trieu chung nen goi y chuyen khoa thieu chinh xac.

## 3. `find_available_doctors(specialty, location, date)`

- **Loi dinh dang thoi gian:** `date` sai format, vi du MM/DD thay vi YYYY-MM-DD, hoac truyen ngay trong qua khu.
- **Khong co ket qua phu hop:** Khong co bac si nao thoa man chuyen khoa, dia diem va ngay kham.
- **Du lieu lich khong cap nhat:** Lich bac si trong he thong khong dong bo voi thuc te, vi du bac si nghi nhung van hien thi con lich.

## 4. `book_appointment(patient_id, doctor_id, time_slot)`

- **Race condition:** Khung gio con trong khi tim kiem nhung bi nguoi khac dat mat truoc khi nguoi dung xac nhan.
- **Loi logic nghiep vu:** Benh nhan dat trung lich voi mot lich kham khac trong cung khung gio.
- **Du lieu khong hop le:** `patient_id`, `doctor_id` hoac `time_slot` khong ton tai/khong hop le.
- **Lich bac si thay doi dot xuat:** Bac si nghi phep hoac ban dot xuat nhung he thong chua cap nhat.

## 5. `cancel_appointment(appointment_id)`

- **Vi pham chinh sach huy lich:** Nguoi dung huy qua sat gio kham, vi du he thong yeu cau huy truoc 24 gio.
- **Trang thai khong hop le:** `appointment_id` khong ton tai, sai ID hoac lich da bi huy truoc do.
- **Khong co quyen huy:** Nguoi dung co huy lich khong thuoc tai khoan cua minh.
- **Loi hoan tien:** Lich da thanh toan nhung he thong hoan tien that bai hoac chua xac dinh duoc chinh sach hoan tien.

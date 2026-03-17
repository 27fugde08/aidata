# Hướng dẫn Sử dụng Hệ thống AIOS (AI Automation OS)

Chào mừng bạn đến với **AIOS**, hệ điều hành tự động hóa dựa trên trí tuệ nhân tạo. Tài liệu này sẽ hướng dẫn bạn cách vận hành và khai thác các tính năng của hệ thống.

## 1. Cấu trúc Thư mục Quan trọng

- `/backend`: Mã nguồn phía máy chủ, nơi xử lý logic nghiệp vụ và điều phối Agent.
- `/frontend`: Giao diện người dùng để tương tác với hệ thống.
- `/spaceofduy`: Không gian làm việc chứa dữ liệu dự án, bộ nhớ và các video đã xử lý.
- `/docs`: Tài liệu kỹ thuật và kiến trúc hệ thống.

## 2. Các Tính năng Cốt lõi

### 2.1. Điều phối Đa tác vụ (Multi-Agent Orchestration)
Hệ thống không chỉ chạy một mô hình AI duy nhất mà điều phối nhiều Agent thực hiện các vai trò khác nhau:
- **Manager**: Phân tích yêu cầu và chia nhỏ công việc.
- **Coder**: Viết mã nguồn dựa trên thiết kế.
- **Reviewer**: Kiểm tra lỗi và tối ưu hóa hiệu suất.

### 2.2. Tự động hóa Video (Video Automation)
Đây là tính năng nổi bật giúp tạo nội dung cho YouTube Shorts và TikTok:
1. **Thu thập**: Tự động tải video từ các nguồn (YouTube).
2. **Xử lý**: Cắt video theo tỷ lệ 9:16, thêm phụ đề (subtitles), và chọn lọc các đoạn highlight (điểm nhấn).
3. **Xuất bản**: Lưu trữ video đã xử lý sẵn sàng để đăng tải.

### 2.3. Hệ thống Bộ nhớ Thông minh
AIOS ghi nhớ những gì nó đã làm thông qua:
- **Vector Memory**: Tìm kiếm ngữ nghĩa trong lịch sử làm việc.
- **Knowledge Graph**: Hiểu mối liên hệ giữa các phần của dự án.

## 3. Cách Bắt đầu

### Bước 1: Cấu hình Môi trường
Đảm bảo bạn đã có tệp `.env` trong thư mục `backend/` với các phím API cần thiết (GEMINI_API_KEY, v.v.).

### Bước 2: Khởi chạy Backend
```bash
cd backend
python main.py
```
Máy chủ sẽ khởi chạy tại cổng `8888`.

### Bước 3: Truy cập Giao diện
Mở `frontend/index.html` trong trình duyệt của bạn để bắt đầu điều khiển hệ thống.

## 4. Quy trình Tạo Video Tự động
Để tạo video ngắn từ một video dài:
1. Gửi yêu cầu qua API hoặc Giao diện với URL video.
2. Agent sẽ phân tích các đoạn hội thoại hoặc hành động thú vị.
3. `Video Engine` sẽ thực hiện cắt (crop) và render video.
4. Kết quả sẽ xuất hiện trong thư mục `spaceofduy/shorts`.

## 5. Lưu ý Bảo mật
- Không bao giờ chia sẻ tệp `.env` hoặc các khóa API.
- Các tác vụ thực thi mã (Sandbox) được chạy trong môi trường kiểm soát để đảm bảo an toàn cho hệ thống vật lý của bạn.

---
*Tài liệu này được soạn thảo bởi AIOS Assistant.*

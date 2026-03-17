# YouTube Shorts Automation

Hệ thống tự động hóa quá trình tạo video ngắn (Shorts/TikTok) từ các kênh YouTube.

## Tính năng
- Scan toàn bộ video từ một channel URL.
- Tải video chất lượng cao bằng `yt-dlp`.
- **MỚI:** Tự động phát hiện layout thông minh (Focus 1 người hoặc Split Screen 2 người cho Podcast/Phỏng vấn).
- **MỚI:** Phân tích Hook & Viral Score nâng cao (giải thích lý do viral, category, emoji gợi ý).
- **MỚI:** Chèn Emoji động vào phụ đề dựa trên ngữ cảnh.
- Tự động phát hiện các phân đoạn nổi bật (Highlights).
- Cắt và crop video sang định dạng dọc (9:16) bằng `ffmpeg`.
- Giao diện web quản lý và xem trước kết quả.

## Cấu trúc dự án
- `backend/`: FastAPI server xử lý logic và video.
- `frontend/`: Giao diện React (TailwindCSS).
- `data/`: Lưu trữ video gốc đã tải về.
- `outputs/shorts/`: Lưu trữ các clip ngắn đã xử lý xong.

## Hướng dẫn cài đặt

### Backend
1. Di chuyển vào thư mục backend:
   ```bash
   cd backend
   ```
2. Cài đặt thư viện:
   ```bash
   pip install -r ../requirements.txt
   ```
3. Chạy server:
   ```bash
   python main.py
   ```

### Frontend
1. Di chuyển vào thư mục frontend:
   ```bash
   cd frontend
   ```
2. Cài đặt dependencies:
   ```bash
   npm install
   ```
3. Khởi chạy:
   ```bash
   npm run dev
   ```

## Yêu cầu hệ thống
- Python 3.10+
- FFmpeg (đã cài đặt trong PATH)
- yt-dlp

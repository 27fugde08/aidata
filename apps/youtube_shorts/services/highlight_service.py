import os
import json
import google.generativeai as genai
from typing import List, Dict
from dotenv import load_dotenv

load_dotenv()

class HighlightService:
    """Hệ thống AI phân tích Hook, Virality Score và tạo tiêu đề TikTok."""
    
    def __init__(self):
        api_key = os.getenv("GOOGLE_API_KEY")
        if api_key:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-1.5-flash')
        else:
            self.model = None

    def analyze_segments(self, segments: List[Dict]) -> List[Dict]:
        if self.model:
            try:
                return self.analyze_with_gemini(segments)
            except Exception as e:
                print(f"❌ Gemini Error: {e}")
                return self.fallback_analysis(segments)
        return self.fallback_analysis(segments)

    def analyze_with_gemini(self, segments: List[Dict]) -> List[Dict]:
        transcript_text = ""
        for i, s in enumerate(segments):
            transcript_text += f"[{s['start']:.2f} - {s['end']:.2f}] {s['text']}\n"

        prompt = f"""
        Bạn là một bậc thầy về Content Viral trên TikTok. 
        Nhiệm vụ: Phân tích transcript video và trích xuất các clip ngắn (30-60s) hoàn hảo.

        Yêu cầu cho mỗi clip:
        1. Hook Detection: Phải bắt đầu bằng một câu nói hoặc sự kiện cực kỳ thu hút trong 3 giây đầu.
        2. Virality Score: Chấm điểm từ 1-100.
        3. TikTok Optimization: 
           - Tạo 1 tiêu đề (Title) cực cháy, gây tò mò.
           - Gợi ý bộ Hashtag phù hợp (bao gồm cả trending và niche).
        4. Layout & Visuals:
           - Xác định xem nên dùng layout nào: "focus" (1 người nói) hay "split_screen" (2 người nói chuyện/phỏng vấn).
           - Gợi ý emoji cho các từ khóa quan trọng để chèn vào phụ đề.

        Định dạng trả về duy nhất là JSON array:
        [
          {{
            "start": float, 
            "end": float, 
            "virality_score": int,
            "virality_explanation": "Tại sao clip này lại viral? (Hook, Emotion, Value)",
            "tiktok_title": "Tiêu đề gây tò mò",
            "hashtags": "#hashtag1 #hashtag2",
            "category": "Education/Comedy/Tech/Finance/...",
            "layout_type": "focus" hoặc "split_screen",
            "emoji_map": {{ "từ_khóa": "emoji" }},
            "accent_color": "yellow/red/green/cyan/white",
            "reason": "Giải thích ngắn gọn"
          }}
        ]

        Transcript:
        {transcript_text}
        """

        response = self.model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(response_mime_type="application/json")
        )
        
        return json.loads(response.text)

    def fallback_analysis(self, segments: List[Dict]) -> List[Dict]:
        return [{"start": 0, "end": 30, "virality_score": 50, "tiktok_title": "Clip mới của bạn", "hashtags": "#shorts", "accent_color": "yellow", "is_podcast": False}]

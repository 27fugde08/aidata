import os
import subprocess
import json
import asyncio
import whisper
import cv2
import numpy as np
import textwrap
from typing import List, Dict, Tuple, Optional
import google.generativeai as genai
from dotenv import load_dotenv
import config
from core.event_engine import events

load_dotenv()

# --- Face Detection Setup ---
try:
    import mediapipe as mp
    from mediapipe.python.solutions import face_detection as mp_face_detection
    HAS_MEDIAPIPE = True
except (ImportError, AttributeError):
    try:
        import mediapipe.solutions.face_detection as mp_face_detection
        HAS_MEDIAPIPE = True
    except (ImportError, AttributeError):
        HAS_MEDIAPIPE = False

class HighlightService:
    """Hệ thống AI phân tích Hook, Virality Score và tạo tiêu đề TikTok."""
    def __init__(self):
        api_key = os.getenv("GOOGLE_API_KEY") or config.GEMINI_API_KEY
        if api_key:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-1.5-flash')
        else:
            self.model = None

    def analyze_segments(self, segments: List[Dict]) -> List[Dict]:
        if self.model:
            try:
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
            except Exception as e:
                print(f"❌ Gemini Error: {e}")
        return [{"start": 0, "end": 30, "virality_score": 50, "tiktok_title": "Clip mới", "hashtags": "#shorts", "accent_color": "yellow", "layout_type": "focus"}]

class SubtitleService:
    def __init__(self):
        self.emoji_map = {"money": "💰", "fire": "🔥", "win": "🏆", "success": "🚀", "idea": "💡", "goal": "🎯", "warning": "⚠️"}
        self.colors = {"yellow": "&H00FFFF&", "red": "&H0000FF&", "green": "&H00FF00&", "cyan": "&HFFFF00&", "white": "&HFFFFFF&"}

    def format_timestamp(self, seconds: float) -> str:
        if seconds < 0: seconds = 0
        h, m, s = int(seconds // 3600), int((seconds % 3600) // 60), int(seconds % 60)
        c = int((seconds % 1) * 100)
        return f"{h}:{m:02d}:{s:02d}.{c:02d}"

    def generate_ass_file(self, segments: List[Dict], output_path: str, start_offset: float = 0, accent_color: str = "yellow", emoji_map: Dict[str, str] = None):
        color_hex = self.colors.get(accent_color, self.colors["yellow"])
        dynamic_emojis = emoji_map if emoji_map else {}
        header = textwrap.dedent(f"""
            [Script Info]
            ScriptType: v4.00+
            PlayResX: 1080
            PlayResY: 1920
            ScaledBorderAndShadow: yes
            [V4+ Styles]
            Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
            Style: Viral,Arial Black,125,{color_hex},{color_hex},&H00000000,&H00000000,-1,0,0,0,100,100,0,0,1,15,5,2,10,10,280,1
            [Events]
            Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
        """).strip()
        lines = [header]
        for seg in segments:
            if 'words' in seg and seg['words']:
                for word_data in seg['words']:
                    w_start, w_end = max(0, word_data['start'] - start_offset), word_data['end'] - start_offset
                    if w_end <= w_start: w_end = w_start + 0.3
                    pop_effect = "{\\fscx80\\fscy80\\t(0,100,\\fscx130\\fscy130)\\t(100,200,\\fscx100\\fscy100)}"
                    raw_word = word_data['word'].strip()
                    clean_word = raw_word.lower().strip(".,?!")
                    emoji = dynamic_emojis.get(clean_word) or self.emoji_map.get(clean_word, "")
                    display_text = f"{raw_word.upper()} {emoji}".strip()
                    lines.append(f"Dialogue: 0,{self.format_timestamp(w_start)},{self.format_timestamp(w_end)},Viral,,0,0,0,,{pop_effect}{display_text}")
        with open(output_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

class FaceService:
    def __init__(self):
        self.face_detection = mp_face_detection.FaceDetection(model_selection=1, min_detection_confidence=0.5) if HAS_MEDIAPIPE else None

    def get_best_crop_center(self, video_path: str, start_time: float, end_time: float, is_podcast: bool = False) -> int:
        cap = cv2.VideoCapture(video_path)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        if not self.face_detection: cap.release(); return width // 2
        fps = cap.get(cv2.CAP_PROP_FPS)
        cap.set(cv2.CAP_PROP_POS_MSEC, start_time * 1000)
        face_x_coords = []
        frame_count, max_frames, sample_rate = 0, int((end_time - start_time) * fps), max(1, int(fps / 5))
        while frame_count < max_frames:
            ret, frame = cap.read()
            if not ret: break
            if frame_count % sample_rate == 0:
                results = self.face_detection.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                if results.detections:
                    best_face = max(results.detections, key=lambda d: d.location_data.relative_bounding_box.width) if is_podcast else results.detections[0]
                    bbox = best_face.location_data.relative_bounding_box
                    face_x_coords.append(int((bbox.xmin + bbox.width / 2) * width))
            frame_count += 1
        cap.release()
        return int(np.median(face_x_coords)) if face_x_coords else width // 2

    def detect_layout_strategy(self, video_path: str, start_time: float, end_time: float) -> str:
        if not self.face_detection: return "focus"
        cap = cv2.VideoCapture(video_path)
        fps = cap.get(cv2.CAP_PROP_FPS)
        cap.set(cv2.CAP_PROP_POS_MSEC, start_time * 1000)
        frame_count, max_frames, sample_rate = 0, int((end_time - start_time) * fps), max(1, int(fps / 2))
        multi_face_count, total_samples = 0, 0
        while frame_count < max_frames:
            ret, frame = cap.read()
            if not ret: break
            if frame_count % sample_rate == 0:
                results = self.face_detection.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                if results.detections and len(results.detections) >= 2:
                    faces = sorted(results.detections, key=lambda d: d.location_data.relative_bounding_box.width, reverse=True)[:2]
                    if abs(faces[0].location_data.relative_bounding_box.xmin - faces[1].location_data.relative_bounding_box.xmin) > 0.2:
                        multi_face_count += 1
                total_samples += 1
            frame_count += 1
        cap.release()
        return "split_screen" if total_samples > 0 and (multi_face_count / total_samples) > 0.5 else "focus"

    def get_split_screen_params(self, video_path: str, start_time: float, end_time: float) -> Tuple[int, int]:
        cap = cv2.VideoCapture(video_path)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        if not self.face_detection: cap.release(); return width // 3, width * 2 // 3
        fps = cap.get(cv2.CAP_PROP_FPS)
        cap.set(cv2.CAP_PROP_POS_MSEC, start_time * 1000)
        l_x, r_x = [], []
        frame_count, max_frames, sample_rate = 0, int((end_time - start_time) * fps), max(1, int(fps / 5))
        while frame_count < max_frames:
            ret, frame = cap.read()
            if not ret: break
            if frame_count % sample_rate == 0:
                results = self.face_detection.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                if results.detections and len(results.detections) >= 2:
                    xs = sorted([int((d.location_data.relative_bounding_box.xmin + d.location_data.relative_bounding_box.width/2) * width) for d in results.detections])
                    l_x.append(xs[0]); r_x.append(xs[-1])
            frame_count += 1
        cap.release()
        return (int(np.median(l_x)) if l_x else width // 3), (int(np.median(r_x)) if r_x else width * 2 // 3)

class VideoEngine:
    def __init__(self, workspace_root: str):
        self.workspace = workspace_root
        self.data_dir = os.path.join(workspace_root, "data")
        self.output_dir = os.path.join(workspace_root, "shorts")
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs(self.output_dir, exist_ok=True)
        self.h_service = HighlightService()
        self.s_service = SubtitleService()
        self.f_service = FaceService()
        self.model = None

    def _get_model(self):
        if self.model is None: self.model = whisper.load_model("base")
        return self.model

    async def download_video(self, url: str, video_id: str) -> str:
        path = os.path.join(self.data_dir, f"{video_id}.mp4")
        if not os.path.exists(path):
            cmd = ["yt-dlp", "-f", "bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best", "-o", path, url]
            process = await asyncio.create_subprocess_exec(*cmd); await process.communicate()
        return path

    async def process_viral_shorts(self, url: str, video_id: str, callback=None):
        await events.emit("VIDEO_PROCESS_START", {"url": url, "video_id": video_id})
        if callback: await callback("Downloading video", 10)
        video_path = await self.download_video(url, video_id)
        
        if callback: await callback("Transcribing and AI Analysis", 30)
        result = self._get_model().transcribe(video_path, word_timestamps=True)
        highlights = self.h_service.analyze_segments(result.get("segments", []))
        all_segments = result.get("segments", [])
        
        await events.emit("VIDEO_HIGHLIGHTS_DETECTED", {"video_id": video_id, "count": len(highlights)})
        
        shorts = []
        if callback: await callback(f"Rendering {len(highlights)} clips", 50)
        for i, h in enumerate(highlights):
            name = f"viral_{video_id}_{i}"
            out = await self.render_short(video_path, h["start"], h["end"], name, all_segments, h.get("layout_type", "auto"), h.get("emoji_map", {}), h.get("accent_color", "yellow"))
            meta = {"name": name, "title": h.get("tiktok_title", "Clip"), "score": h.get("virality_score", 0), "category": h.get("category", "General"), "explanation": h.get("virality_explanation", ""), "layout_type": h.get("layout_type", "focus"), "video_url": f"/api/video/stream/shorts/{name}.mp4"}
            shorts.append(meta)
            with open(os.path.join(self.output_dir, f"{name}.json"), "w", encoding="utf-8") as f: json.dump(meta, f, ensure_ascii=False, indent=2)
            await events.emit("SHORT_RENDERED", {"name": name, "video_id": video_id})

        if callback: await callback("Completed", 100)
        await events.emit("VIDEO_PROCESS_COMPLETED", {"video_id": video_id, "shorts_count": len(shorts)})
        return shorts

    async def render_short(self, video_path: str, start: float, end: float, output_name: str, segments: List[Dict], layout: str, emoji_map: Dict, color: str):
        out_path = os.path.join(self.output_dir, f"{output_name}.mp4")
        ass_path = os.path.join(self.output_dir, f"{output_name}.ass")
        cap = cv2.VideoCapture(video_path); vw, vh = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)); cap.release()
        if layout == "auto": layout = self.f_service.detect_layout_strategy(video_path, start, end)
        duration = end - start
        ass_safe = ass_path.replace("\\", "/").replace(":", "\\:")
        p_bar = f"drawbox=y=ih-15:color=0x6366f1:width=iw*t/{duration}:height=15:t=fill"
        if layout == "split_screen":
            l_x, r_x = self.f_service.get_split_screen_params(video_path, start, end)
            cw = min(vw, int(vh * 1.125))
            def get_c(cx):
                x = max(0, min(vw - cw, cx - cw // 2))
                return f"crop={cw}:{vh}:{x}:0,scale=1080:960"
            vf = f"[0:v]{get_c(l_x)}[t];[0:v]{get_c(r_x)}[b];[t][b]vstack,{p_bar},ass='{ass_safe}'"
        else:
            fx = self.f_service.get_best_crop_center(video_path, start, end)
            tw = int(vh * 9 / 16); xs = max(0, min(vw - tw, fx - tw // 2))
            zl = "if(lt(mod(t\\,8)\\,4)\\,1.0\\,1.1)"
            vf = f"crop={tw}:{vh}:{xs}:0,crop=iw/{zl}:ih/{zl}:(iw-ow)/2:(ih-oh)/2,scale=1080:1920,{p_bar},ass='{ass_safe}'"
        
        rel_segs = []
        for s in segments:
            if s['start'] < end and s['end'] > start:
                ns = s.copy()
                if 'words' in s: ns['words'] = [w for w in s['words'] if w['start'] >= start and w['end'] <= end]
                rel_segs.append(ns)
        self.s_service.generate_ass_file(rel_segs, ass_path, start, color, emoji_map)
        cmd = ["ffmpeg", "-y", "-ss", str(start), "-i", video_path, "-t", str(duration), "-filter_complex", vf, "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-c:a", "aac", "-b:a", "192k", out_path]
        proc = await asyncio.create_subprocess_exec(*cmd); await proc.communicate()
        return out_path

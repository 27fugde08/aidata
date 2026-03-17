import os
import subprocess
import json
import asyncio
import whisper
import cv2
from typing import List, Dict
from .highlight_service import HighlightService
from .subtitle_service import SubtitleService
from .face_service import FaceService

class VideoService:
    def __init__(self):
        self.root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
        self.data_dir = os.path.join(self.root, "data")
        self.output_dir = os.path.join(self.root, "outputs/shorts")
        self.export_dir = os.path.join(self.root, "outputs/tiktok_export")
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(self.export_dir, exist_ok=True)
        
        self.h_service = HighlightService()
        self.s_service = SubtitleService()
        self.f_service = FaceService()
        self.model = None

    def _get_model(self):
        if self.model is None:
            self.model = whisper.load_model("base")
        return self.model

    async def scan_channel(self, channel_url: str) -> List[Dict]:
        cmd = ["yt-dlp", "--flat-playlist", "--dump-single-json", "--playlist-end", "10", channel_url]
        process = await asyncio.create_subprocess_exec(*cmd, stdout=asyncio.subprocess.PIPE)
        stdout, _ = await process.communicate()
        data = json.loads(stdout.decode())
        return [{"id": e["id"], "title": e["title"], "url": f"https://youtube.com/watch?v={e['id']}", "thumbnail": e.get("thumbnails", [{}])[-1].get("url")} for e in data.get("entries", [])]

    async def download_video(self, video_url: str, video_id: str) -> str:
        path = os.path.join(self.data_dir, f"{video_id}.mp4")
        if not os.path.exists(path):
            cmd = ["yt-dlp", "-f", "bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best", "-o", path, video_url]
            process = await asyncio.create_subprocess_exec(*cmd); await process.communicate()
        return path

    async def detect_highlights_semantic(self, video_path: str) -> Dict:
        model = self._get_model()
        result = model.transcribe(video_path, word_timestamps=True)
        segments = result.get("segments", [])
        highlights = self.h_service.analyze_segments(segments)
        return {
            "highlights": highlights,
            "all_segments": segments
        }

    async def render_short_with_subs(self, video_path: str, start: float, end: float, output_name: str, all_segments: List[Dict], is_podcast: bool = False, accent_color: str = "yellow", layout_type: str = "auto", emoji_map: Dict = None):
        out_path = os.path.join(self.output_dir, f"{output_name}.mp4")
        tiktok_path = os.path.join(self.export_dir, f"TIKTOK_{output_name}.mp4")
        ass_path = os.path.join(self.output_dir, f"{output_name}.ass")

        cap = cv2.VideoCapture(video_path)
        vw = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        vh = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        cap.release()

        # Determine layout
        if layout_type == "auto":
            layout_type = self.f_service.detect_layout_strategy(video_path, start, end)
        
        vf = ""
        duration = end - start
        ass_safe_path = ass_path.replace("\\", "/").replace(":", "\\:")
        progress_bar = f"drawbox=y=ih-15:color=0x6366f1:width=iw*t/{duration}:height=15:t=fill"

        if layout_type == "split_screen":
            # Split Screen Logic: Top (Left Person) / Bottom (Right Person)
            left_x, right_x = self.f_service.get_split_screen_params(video_path, start, end)
            
            # Target per half: 1080x960. Aspect Ratio = 1.125
            crop_h = vh
            crop_w = int(vh * 1.125)
            if crop_w > vw: crop_w = vw
            
            # Calculate crop boxes
            def get_crop_filter(center_x):
                x = center_x - (crop_w // 2)
                if x < 0: x = 0
                elif x + crop_w > vw: x = vw - crop_w
                return f"crop={crop_w}:{crop_h}:{x}:0,scale=1080:960"

            top_crop = get_crop_filter(left_x)
            bottom_crop = get_crop_filter(right_x)
            
            vf = (
                f"[0:v]{top_crop}[top];"
                f"[0:v]{bottom_crop}[bottom];"
                f"[top][bottom]vstack,"
                f"{progress_bar},"
                f"ass='{ass_safe_path}'"
            )
        else:
            # Standard Focus Mode
            face_x = self.f_service.get_best_crop_center(video_path, start, end, is_podcast=is_podcast)
            crop_filter = self.f_service.calculate_crop_params(vw, vh, face_x)
            # Escape commas for ffmpeg filter chain
            zoom_logic = "if(lt(mod(t\\,8)\\,4)\\,1.0\\,1.1)"
            
            vf = (
                f"{crop_filter},"
                f"crop=iw/{zoom_logic}:ih/{zoom_logic}:(iw-ow)/2:(ih-oh)/2,"
                f"scale=1080:1920,"
                f"{progress_bar},"
                f"ass='{ass_safe_path}'"
            )

        relevant_segments = []
        for seg in all_segments:
            if seg['start'] < end and seg['end'] > start:
                new_seg = seg.copy()
                if 'words' in seg:
                    new_seg['words'] = [w for w in seg['words'] if w['start'] >= start and w['end'] <= end]
                relevant_segments.append(new_seg)

        self.s_service.generate_ass_file(relevant_segments, ass_path, start_offset=start, accent_color=accent_color, emoji_map=emoji_map)
        
        cmd = [
            "ffmpeg", "-y", "-ss", str(start), "-i", video_path,
            "-t", str(end - start),
            "-filter_complex", vf,
            "-c:v", "libx264", "-profile:v", "high", "-level", "4.2", "-pix_fmt", "yuv420p",
            "-preset", "veryfast", "-crf", "20",
            "-c:a", "aac", "-b:a", "192k",
            out_path
        ]
        process = await asyncio.create_subprocess_exec(*cmd); await process.communicate()
        if os.path.exists(out_path):
            import shutil
            shutil.copy2(out_path, tiktok_path)
        return out_path

    async def concatenate_clips(self, clip_paths: List[str], output_name: str) -> str:
        """Gộp nhiều clip đã render thành một clip duy nhất."""
        out_path = os.path.join(self.output_dir, f"{output_name}.mp4")
        tiktok_path = os.path.join(self.export_dir, f"MERGED_{output_name}.mp4")
        list_path = os.path.join(self.output_dir, f"{output_name}_list.txt")
        with open(list_path, "w", encoding="utf-8") as f:
            for p in clip_paths:
                abs_p = os.path.abspath(p).replace("\\", "/")
                f.write(f"file '{abs_p}'\n")
        cmd = ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", list_path, "-c", "copy", out_path]
        process = await asyncio.create_subprocess_exec(*cmd); await process.communicate()
        if os.path.exists(out_path):
            import shutil
            shutil.copy2(out_path, tiktok_path)
            try: os.remove(list_path)
            except: pass
            return out_path
        return None

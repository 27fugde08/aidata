import os
import textwrap
from typing import List, Dict

class SubtitleService:
    """Module tạo hiệu ứng phụ đề 'Pop-in' và 'Emotion-based Colors' phong cách TikTok Viral."""

    def __init__(self):
        self.emoji_map = {"money": "💰", "fire": "🔥", "win": "🏆", "success": "🚀", "idea": "💡", "goal": "🎯", "warning": "⚠️"}
        # Mapping các màu sắc (Định dạng &H BGR &)
        self.colors = {
            "yellow": "&H00FFFF&",
            "red": "&H0000FF&",
            "green": "&H00FF00&",
            "cyan": "&HFFFF00&",
            "white": "&HFFFFFF&"
        }

    def format_timestamp(self, seconds: float) -> str:
        if seconds < 0: seconds = 0
        h = int(seconds // 3600)
        m = int((seconds % 3600) // 60)
        s = int(seconds % 60)
        c = int((seconds % 1) * 100)
        return f"{h}:{m:02d}:{s:02d}.{c:02d}"

    def generate_ass_file(self, segments: List[Dict], output_path: str, start_offset: float = 0, accent_color: str = "yellow", emoji_map: Dict[str, str] = None):
        """
        Tạo file .ass với hiệu ứng Pop-in:
        - {\t(0,100,\fscx120\fscy120)}: Phóng to 120% trong 100ms đầu.
        - {\t(100,200,\fscx100\fscy100)}: Thu nhỏ về 100% trong 100ms tiếp theo.
        """
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
            # Alignment 2 = Bottom Center. MarginV 280 = Đưa lên trên thanh công cụ TikTok
            Style: Default,Arial Black,110,&H00FFFFFF,&H0000FFFF,&H00000000,&H00000000,-1,0,0,0,100,100,0,0,1,12,4,2,10,10,280,1
            Style: Viral,Arial Black,125,{color_hex},{color_hex},&H00000000,&H00000000,-1,0,0,0,100,100,0,0,1,15,5,2,10,10,280,1

            [Events]
            Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
        """).strip()

        lines = [header]
        
        for seg in segments:
            if 'words' in seg and seg['words']:
                for word_data in seg['words']:
                    w_start = max(0, word_data['start'] - start_offset)
                    w_end = word_data['end'] - start_offset
                    if w_end <= w_start: w_end = w_start + 0.3

                    # Hiệu ứng Pop-in Animation tag:
                    # Phóng to từ 80% lên 130% rồi về 100%
                    pop_effect = "{\\fscx80\\fscy80\\t(0,100,\\fscx130\\fscy130)\\t(100,200,\\fscx100\\fscy100)}"
                    
                    raw_word = word_data['word'].strip()
                    clean_word = raw_word.lower().strip(".,?!")
                    
                    # Check dynamic map first, then static map
                    emoji = dynamic_emojis.get(clean_word) or self.emoji_map.get(clean_word, "")
                    
                    display_text = raw_word.upper()
                    if emoji:
                        display_text += f" {emoji}"
                    
                    lines.append(f"Dialogue: 0,{self.format_timestamp(w_start)},{self.format_timestamp(w_end)},Viral,,0,0,0,,{pop_effect}{display_text}")
            else:
                # Fallback logic chia cụm từ nếu không có word-level
                pass

        with open(output_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        return output_path

    def get_tiktok_vfilter(self, ass_path: str) -> str:
        safe_path = ass_path.replace("\\", "/").replace(":", "\\:")
        return f"crop=ih*9/16:ih,scale=1080:1920,ass='{safe_path}'"

import cv2
import numpy as np
from typing import List, Tuple, Optional

# Cố gắng import MediaPipe một cách an toàn
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

class FaceService:
    """Module phát hiện khuôn mặt để tự động crop video 9:16 thông minh."""
    
    def __init__(self):
        self.face_detection = None
        if HAS_MEDIAPIPE:
            try:
                self.face_detection = mp_face_detection.FaceDetection(
                    model_selection=1,
                    min_detection_confidence=0.5
                )
            except Exception as e:
                print(f"⚠️ MediaPipe FaceDetection failed to init: {e}")
                self.face_detection = None

    def get_best_crop_center(self, video_path: str, start_time: float, end_time: float, is_podcast: bool = False) -> int:
        """
        Phân tích đoạn clip để tìm tọa độ X tốt nhất.
        Nếu is_podcast=True, sẽ ưu tiên người đang nói (khuôn mặt có sự thay đổi hoặc to nhất).
        """
        cap = cv2.VideoCapture(video_path)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        
        if not HAS_MEDIAPIPE or self.face_detection is None:
            cap.release()
            return width // 2

        fps = cap.get(cv2.CAP_PROP_FPS)
        cap.set(cv2.CAP_PROP_POS_MSEC, start_time * 1000)
        
        face_x_coords = []
        frame_count = 0
        max_frames = int((end_time - start_time) * fps)
        sample_rate = max(1, int(fps / 5))
        
        while frame_count < max_frames:
            ret, frame = cap.read()
            if not ret: break
            
            if frame_count % sample_rate == 0:
                try:
                    results = self.face_detection.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                    if results.detections:
                        # Nếu là Podcast, tìm khuôn mặt to nhất (thường là người đang nói gần mic)
                        if is_podcast:
                            best_face = max(results.detections, key=lambda d: d.location_data.relative_bounding_box.width)
                        else:
                            best_face = results.detections[0]
                            
                        bbox = best_face.location_data.relative_bounding_box
                        center_x = int((bbox.xmin + bbox.width / 2) * width)
                        face_x_coords.append(center_x)
                except: pass
            
            frame_count += 1
            
        cap.release()
        return int(np.median(face_x_coords)) if face_x_coords else width // 2

    def detect_layout_strategy(self, video_path: str, start_time: float, end_time: float) -> str:
        """
        Xác định xem nên dùng layout 'focus' hay 'split_screen'.
        Nếu phát hiện 2 khuôn mặt cách xa nhau trong phần lớn thời gian -> split_screen.
        """
        if not HAS_MEDIAPIPE or self.face_detection is None:
            return "focus"

        cap = cv2.VideoCapture(video_path)
        fps = cap.get(cv2.CAP_PROP_FPS)
        cap.set(cv2.CAP_PROP_POS_MSEC, start_time * 1000)
        
        frame_count = 0
        max_frames = int((end_time - start_time) * fps)
        sample_rate = max(1, int(fps / 2)) # Sample mỗi 0.5s
        
        multi_face_count = 0
        total_samples = 0
        
        while frame_count < max_frames:
            ret, frame = cap.read()
            if not ret: break
            
            if frame_count % sample_rate == 0:
                try:
                    results = self.face_detection.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                    if results.detections and len(results.detections) >= 2:
                        # Kiểm tra khoảng cách giữa 2 khuôn mặt lớn nhất
                        faces = sorted(results.detections, key=lambda d: d.location_data.relative_bounding_box.width, reverse=True)[:2]
                        x1 = faces[0].location_data.relative_bounding_box.xmin
                        x2 = faces[1].location_data.relative_bounding_box.xmin
                        if abs(x1 - x2) > 0.2: # Cách nhau ít nhất 20% khung hình
                            multi_face_count += 1
                    total_samples += 1
                except: pass
            
            frame_count += 1
            
        cap.release()
        
        # Nếu hơn 50% mẫu có 2 khuôn mặt -> Split Screen
        if total_samples > 0 and (multi_face_count / total_samples) > 0.5:
            return "split_screen"
        return "focus"

    def get_split_screen_params(self, video_path: str, start_time: float, end_time: float) -> Tuple[int, int]:
        """
        Trả về tọa độ trung tâm X của người bên trái (cho Top) và người bên phải (cho Bottom).
        """
        cap = cv2.VideoCapture(video_path)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        
        if not HAS_MEDIAPIPE or self.face_detection is None:
            cap.release()
            return width // 3, width * 2 // 3

        fps = cap.get(cv2.CAP_PROP_FPS)
        cap.set(cv2.CAP_PROP_POS_MSEC, start_time * 1000)
        
        left_faces_x = []
        right_faces_x = []
        
        frame_count = 0
        max_frames = int((end_time - start_time) * fps)
        sample_rate = max(1, int(fps / 5))
        
        while frame_count < max_frames:
            ret, frame = cap.read()
            if not ret: break
            
            if frame_count % sample_rate == 0:
                try:
                    results = self.face_detection.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                    if results.detections and len(results.detections) >= 2:
                        faces = []
                        for det in results.detections:
                            bbox = det.location_data.relative_bounding_box
                            cx = int((bbox.xmin + bbox.width / 2) * width)
                            faces.append(cx)
                        
                        faces.sort()
                        # Giả định 2 khuôn mặt chính là 2 người ngoài cùng trái/phải
                        if len(faces) >= 2:
                            left_faces_x.append(faces[0])
                            right_faces_x.append(faces[-1])
                except: pass
            frame_count += 1
            
        cap.release()
        
        left_x = int(np.median(left_faces_x)) if left_faces_x else width // 3
        right_x = int(np.median(right_faces_x)) if right_faces_x else width * 2 // 3
        
        return left_x, right_x

    def calculate_crop_params(self, video_width: int, video_height: int, face_x: int) -> str:
        """Tính toán chuỗi filter crop cho FFmpeg."""
        target_w = int(video_height * 9 / 16)
        x_start = face_x - (target_w // 2)
        if x_start < 0: x_start = 0
        elif x_start + target_w > video_width: x_start = video_width - target_w
        return f"crop={target_w}:{video_height}:{x_start}:0"

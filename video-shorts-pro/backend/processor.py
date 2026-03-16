import ffmpeg
import os

class ProcessorService:
    def __init__(self, output_dir="shorts"):
        self.output_dir = output_dir
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def process_short(self, input_path, start_time, end_time):
        """
        Trims, crops to 9:16 (vertical), and compresses video.
        """
        if not os.path.exists(input_path):
            return {"error": f"Input file not found: {input_path}"}

        filename = os.path.basename(input_path)
        output_filename = f"short_{start_time}_{end_time}_{filename}"
        output_path = os.path.join(self.output_dir, output_filename)

        try:
            # 1. Probe for resolution
            probe = ffmpeg.probe(input_path)
            video_stream = next((stream for stream in probe['streams'] if stream['codec_type'] == 'video'), None)
            width = int(video_stream['width'])
            height = int(video_stream['height'])

            # 2. Calculate crop for 9:16 center
            # Target 9:16 means width = height * (9/16)
            target_width = int(height * (9 / 16))
            if target_width > width:
                # If original width is smaller than target 9:16 width,
                # we crop by height instead: height = width * (16/9)
                target_width = width
                target_height = int(width * (16 / 9))
                x = 0
                y = (height - target_height) // 2
                crop_params = f"crop={target_width}:{target_height}:{x}:{y}"
            else:
                target_height = height
                x = (width - target_width) // 2
                y = 0
                crop_params = f"crop={target_width}:{target_height}:{x}:{y}"

            # 3. Build FFmpeg command
            (
                ffmpeg
                .input(input_path, ss=start_time, to=end_time)
                .filter('vf', crop_params)
                .output(output_path, vcodec='libx264', acodec='aac', strict='experimental', crf=23, preset='fast')
                .overwrite_output()
                .run()
            )

            return {"status": "success", "output_path": output_path}
        except Exception as e:
            return {"status": "error", "error": str(e)}

    def list_shorts(self):
        return [f for f in os.listdir(self.output_dir) if f.endswith(".mp4")]

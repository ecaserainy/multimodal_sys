import subprocess
from pathlib import Path

def convert_to_wav(source_path: str, target_path: str):
    command = [
        "ffmpeg",
        "-i", source_path,
        "-ar", "16000",
        "-ac", "1",
        "-y",
        target_path
    ]
    result = subprocess.run(command, capture_output=True)
    if result.returncode != 0:
        raise RuntimeError(f"音频转换失败: {result.stderr.decode()}")
    return target_path

def validate_audio_file(file_path: str) -> bool:
    suffix = Path(file_path).suffix.lower()
    return suffix in [".wav", ".mp3", ".m4a", ".flac", ".ogg"]

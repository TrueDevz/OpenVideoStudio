import os
from datetime import timedelta

try:
    import whisper
except ImportError:
    whisper = None

def generate_srt(audio_path: str, output_srt_path: str, model_size: str = "base"):
    """
    Transcribes the audio file and generates an SRT subtitle file.
    Uses local Whisper model.
    """
    if not whisper:
        raise ImportError("openai-whisper package is not installed.")
        
    print(f"Loading Whisper model ({model_size})...")
    model = whisper.load_model(model_size)
    
    print(f"Transcribing {audio_path}...")
    # transcribe with word-level timestamps (for better subtitle syncing) if needed, 
    # but basic transcribe works fine for standard SRT.
    result = model.transcribe(audio_path)
    
    # Generate SRT format
    srt_content = ""
    for i, segment in enumerate(result["segments"], start=1):
        start_time = _format_timestamp(segment["start"])
        end_time = _format_timestamp(segment["end"])
        text = segment["text"].strip()
        
        srt_content += f"{i}\n"
        srt_content += f"{start_time} --> {end_time}\n"
        srt_content += f"{text}\n\n"
        
    # Ensure directory exists
    os.makedirs(os.path.dirname(os.path.abspath(output_srt_path)), exist_ok=True)
    
    with open(output_srt_path, "w", encoding="utf-8") as f:
        f.write(srt_content)
        
    print(f"SRT saved to {output_srt_path}")
    return output_srt_path

def _format_timestamp(seconds: float) -> str:
    """Formats seconds into SRT timestamp format: HH:MM:SS,mmm"""
    td = timedelta(seconds=seconds)
    hours = td.seconds // 3600
    minutes = (td.seconds % 3600) // 60
    seconds = td.seconds % 60
    milliseconds = td.microseconds // 1000
    return f"{hours:02d}:{minutes:02d}:{seconds:02d},{milliseconds:03d}"

# For local testing
if __name__ == "__main__":
    # Ensure you have a test_audio.mp3
    # generate_srt("test_audio.mp3", "test_subtitles.srt")
    pass

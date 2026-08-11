import os
try:
    from moviepy.editor import VideoFileClip, AudioFileClip, concatenate_videoclips
except ImportError:
    pass

def compose_video(video_paths: list[str], audio_path: str, output_path: str, srt_path: str = None) -> str:
    """
    Composes a final video by concatenating video clips and overlaying audio.
    Assumes moviepy and ffmpeg are installed on the system.
    """
    try:
        from moviepy.editor import VideoFileClip, AudioFileClip, concatenate_videoclips
    except ImportError:
        raise ImportError("moviepy is not installed. Please install it to use video composition.")
        
    print("Loading video clips...")
    clips = []
    for path in video_paths:
        if os.path.exists(path):
            # Load and resize to 9:16 (1080x1920) if needed, for simplicity we just load it here
            clip = VideoFileClip(path)
            clips.append(clip)
        else:
            print(f"Warning: Video not found at {path}")
            
    if not clips:
        raise ValueError("No valid video clips found to compose.")

    print("Concatenating clips...")
    final_video = concatenate_videoclips(clips, method="compose")
    
    print("Adding audio track...")
    if os.path.exists(audio_path):
        audio = AudioFileClip(audio_path)
        # Ensure video length matches audio length
        final_video = final_video.set_audio(audio).set_duration(audio.duration)
    else:
        print(f"Warning: Audio not found at {audio_path}. Proceeding without audio.")

    # Ensure output directory exists
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    
    print(f"Exporting final video to {output_path}...")
    # Using ffmpeg underneath. Subtitles can be burned in using ffmpeg directly if needed,
    # but moviepy TextClip can also be used. For simplicity and robustness, 
    # we export without burned-in subs first, then use raw ffmpeg for SRT burning if provided.
    
    temp_output = output_path.replace(".mp4", "_temp.mp4")
    final_video.write_videofile(temp_output, fps=24, codec="libx264", audio_codec="aac")
    
    # Close clips to free memory
    for clip in clips:
        clip.close()
    if 'audio' in locals():
        audio.close()
    final_video.close()
    
    # If SRT is provided, burn it in using raw ffmpeg command
    if srt_path and os.path.exists(srt_path):
        print(f"Burning subtitles from {srt_path}...")
        # Escape path for ffmpeg filter
        srt_escaped = srt_path.replace("\\", "/").replace(":", "\\:")
        ffmpeg_cmd = f'ffmpeg -y -i "{temp_output}" -vf subtitles="{srt_escaped}" "{output_path}"'
        os.system(ffmpeg_cmd)
        
        # Cleanup temp
        if os.path.exists(output_path):
            os.remove(temp_output)
    else:
        # Just rename temp to final
        os.rename(temp_output, output_path)

    return output_path

# For local testing
if __name__ == "__main__":
    pass

import asyncio
import os
try:
    import edge_tts
except ImportError:
    edge_tts = None

# Good voices for Indian context:
# Telugu Female: te-IN-ShrutiNeural
# Telugu Male: te-IN-MohanNeural
# English India Female: en-IN-NeerjaNeural
# English India Male: en-IN-PrabhatNeural

async def generate_audio_async(text: str, output_path: str, language: str = "te") -> str:
    if not edge_tts:
        raise ImportError("edge-tts package is not installed.")
        
    # Select voice based on language
    if language.lower().startswith("te"):
        voice = "te-IN-ShrutiNeural" # Default to female Telugu voice
    else:
        voice = "en-IN-PrabhatNeural" # Default to English Indian accent
        
    communicate = edge_tts.Communicate(text, voice)
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    
    await communicate.save(output_path)
    return output_path

def generate_audio(text: str, output_path: str, language: str = "te") -> str:
    """
    Generates speech audio from text using Edge-TTS.
    Saves the audio to output_path (should be .mp3).
    """
    return asyncio.run(generate_audio_async(text, output_path, language))

# For local testing
if __name__ == "__main__":
    # test_text = "నమస్కారం, ఇది ఓపెన్ వీడియో స్టూడియో ద్వారా సృష్టించబడిన ఆడియో."
    # generate_audio(test_text, "test_output.mp3", language="te")
    # print("Audio saved to test_output.mp3")
    pass

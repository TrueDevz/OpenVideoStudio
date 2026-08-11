import json
import os

try:
    import google.generativeai as genai
except ImportError:
    genai = None

try:
    import ollama
except ImportError:
    ollama = None

def generate_video_plan(prompt: str, duration: int = 15, provider: str = "gemini", api_key: str = None) -> dict:
    """
    Generates a structured video plan (scenes, script, asset queries) based on the user's prompt.
    Returns a dictionary parsed from JSON.
    """
    
    system_prompt = f"""
    You are an expert AI video producer. The user wants to create a {duration}-second video based on the following idea: "{prompt}".
    Respond ONLY with a valid JSON object matching this schema. Do not include markdown formatting or extra text.
    
    Schema:
    {{
      "title": "Short catchy title",
      "language": "Detect the language of the prompt and use it for the narration (e.g., Telugu, English)",
      "scenes": [
        {{
          "scene_number": 1,
          "duration": 4,
          "narration_text": "The exact script to be spoken in this scene in the detected language.",
          "visual_description": "A short English description of what should be shown on screen.",
          "search_query": "A 1-3 word English search query to find stock footage for this scene on Pexels (e.g., 'artificial intelligence', 'happy family')."
        }}
      ]
    }}
    
    Ensure the total duration of all scenes adds up to approximately {duration} seconds. Keep narration concise enough to fit in the scene duration.
    """

    if provider == "gemini":
        if not genai:
            raise ImportError("google-generativeai package is not installed.")
        if not api_key:
            api_key = os.environ.get("GEMINI_API_KEY")
            if not api_key:
                raise ValueError("Gemini API key is required but not provided or found in environment variables.")
                
        genai.configure(api_key=api_key)
        
        # Try finding an available model, favoring 1.5 flash
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        
        # Priority order for models
        preferred_models = ['models/gemini-1.5-flash', 'models/gemini-1.5-flash-latest', 'models/gemini-pro', 'models/gemini-1.0-pro']
        selected_model = None
        
        for pref in preferred_models:
            if pref in available_models:
                selected_model = pref
                break
                
        if not selected_model:
            selected_model = available_models[0] if available_models else 'gemini-1.5-flash'
            
        print(f"Using Gemini model: {selected_model}")
        
        # response_mime_type is supported in 1.5 models. For 1.0 pro we just use normal generation.
        generation_config = {"response_mime_type": "application/json"} if "1.5" in selected_model else {}
        
        model = genai.GenerativeModel(selected_model, generation_config=generation_config)
        response = model.generate_content(system_prompt)
        
        try:
            return json.loads(response.text)
        except json.JSONDecodeError:
            raise ValueError(f"Failed to parse JSON from Gemini response: {response.text}")

    elif provider == "ollama":
        if not ollama:
            raise ImportError("ollama package is not installed.")
            
        # We assume a local ollama instance is running. 'llama3' is a good default.
        response = ollama.chat(model='llama3', messages=[
            {
                'role': 'system',
                'content': system_prompt
            },
            {
                'role': 'user',
                'content': "Generate the JSON plan now."
            }
        ])
        
        content = response['message']['content']
        # Cleanup potential markdown if the model disobeys instructions
        if content.startswith("```json"):
            content = content.replace("```json", "").replace("```", "").strip()
            
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            raise ValueError(f"Failed to parse JSON from Ollama response: {content}")
            
    else:
        raise ValueError(f"Unsupported LLM provider: {provider}")

# For local testing
if __name__ == "__main__":
    # Ensure you set GEMINI_API_KEY environment variable before running this test
    # test_prompt = "మన రోజువారీ జీవితంలో Artificial Intelligence ఎలా ఉపయోగపడుతుంది?"
    # print(json.dumps(generate_video_plan(test_prompt, provider="gemini"), indent=2, ensure_ascii=False))
    pass

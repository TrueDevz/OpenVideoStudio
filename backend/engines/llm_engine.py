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
        # Use gemini-1.5-flash as it's fast, free-tier friendly, and great at JSON
        model = genai.GenerativeModel('gemini-1.5-flash', generation_config={"response_mime_type": "application/json"})
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

# OpenVideoStudio 🎬

![OpenVideoStudio](https://img.shields.io/badge/Open-Source-brightgreen.svg)
![License](https://img.shields.io/badge/License-MIT-blue.svg)

OpenVideoStudio is a 100% free, open-source AI Video Production Studio. It allows you to create short-form videos (like YouTube Shorts or Instagram Reels) from just a simple text idea, using entirely free or local AI models.

## Features ✨
- **AI Script Generation:** Uses Google Gemini (Free Tier) or Ollama (Local) to generate scenes and narration.
- **Local TTS:** Uses Edge-TTS for high-quality, free voiceovers (Supports Telugu, English, and more).
- **Free Stock Assets:** Automatically fetches relevant video clips from Pexels API.
- **Auto Subtitles:** Generates perfectly timed `.srt` files using OpenAI Whisper locally.
- **Auto Editing:** Composes the final video automatically using FFmpeg & MoviePy.

## How to use in Google Colab (Recommended) ☁️
The easiest way to use OpenVideoStudio without installing anything is via Google Colab.
1. Upload the `OpenVideoStudio_Colab.ipynb` to Google Colab.
2. Enter your free API keys (Gemini, Pexels) in the designated cells.
3. Run all cells to get a public URL where you can access the web interface!

## How to run locally (Windows/Mac/Linux) 💻

### Prerequisites
- Python 3.9+
- FFmpeg installed and added to your system PATH.

### Setup
1. Clone the repository:
   ```bash
   git clone https://github.com/YOUR_USERNAME/OpenVideoStudio.git
   cd OpenVideoStudio/backend
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set your environment variables:
   ```bash
   # On Windows
   set GEMINI_API_KEY=your_key_here
   set PEXELS_API_KEY=your_key_here
   ```
4. Run the server:
   ```bash
   python main.py
   ```
5. Open `http://localhost:8000` in your browser!

## Built With 🛠️
- **Frontend:** Vanilla HTML/CSS/JS (Zero build steps!)
- **Backend:** Python FastAPI
- **AI/Media Engines:** Gemini/Ollama, Edge-TTS, Whisper, MoviePy, FFmpeg

## License 📄
This project is licensed under the MIT License.

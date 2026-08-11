import os
import requests

PEXELS_API_KEY = os.environ.get("PEXELS_API_KEY")
PEXELS_BASE_URL = "https://api.pexels.com/videos/search"

def search_stock_video(query: str, orientation: str = "portrait", size: str = "medium") -> str:
    """
    Searches for a stock video on Pexels and returns the best video URL.
    orientation: 'portrait' (9:16), 'landscape' (16:9), or 'square'
    """
    if not PEXELS_API_KEY:
        print("WARNING: PEXELS_API_KEY not found. Using a fallback placeholder video.")
        return "https://www.w3schools.com/html/mov_bbb.mp4" # Fallback test video
        
    headers = {
        "Authorization": PEXELS_API_KEY
    }
    params = {
        "query": query,
        "orientation": orientation,
        "size": size,
        "per_page": 1
    }
    
    try:
        response = requests.get(PEXELS_BASE_URL, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        
        if data.get("videos") and len(data["videos"]) > 0:
            video_files = data["videos"][0].get("video_files", [])
            # Try to find an HD version
            best_file = None
            for f in video_files:
                if f.get("quality") == "hd":
                    best_file = f
                    break
            
            if not best_file and video_files:
                best_file = video_files[0]
                
            if best_file:
                return best_file.get("link")
                
    except Exception as e:
        print(f"Error fetching from Pexels API: {e}")
        
    # Fallback if search fails
    return "https://www.w3schools.com/html/mov_bbb.mp4"

def download_video(url: str, output_path: str):
    """
    Downloads a video from a URL to the local disk.
    """
    # Ensure directory exists
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192): 
                f.write(chunk)
        return output_path
    except Exception as e:
        print(f"Error downloading video: {e}")
        return None

# For local testing
if __name__ == "__main__":
    # print(search_stock_video("artificial intelligence"))
    pass

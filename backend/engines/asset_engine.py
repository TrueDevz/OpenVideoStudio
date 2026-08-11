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
    def fetch_pexels(q: str, orient: str = None) -> str:
        headers = {"Authorization": PEXELS_API_KEY}
        params = {"query": q, "size": size, "per_page": 15} # Fetch more to pick the best HD
        if orient:
            params["orientation"] = orient
            
        try:
            response = requests.get(PEXELS_BASE_URL, headers=headers, params=params)
            response.raise_for_status()
            data = response.json()
            
            if data.get("videos") and len(data["videos"]) > 0:
                # Pick the first video and find its HD file
                video_files = data["videos"][0].get("video_files", [])
                best_file = next((f for f in video_files if f.get("quality") == "hd"), None)
                if not best_file and video_files:
                    best_file = video_files[0]
                if best_file:
                    return best_file.get("link")
        except Exception as e:
            print(f"Error fetching from Pexels API for '{q}': {e}")
        return None

    # Strategy 1: Try exact query with portrait orientation
    result = fetch_pexels(query, orientation)
    if result: return result
    
    print(f"No portrait results for '{query}'. Retrying without orientation...")
    # Strategy 2: Try exact query, any orientation
    result = fetch_pexels(query, None)
    if result: return result
    
    print(f"No results for '{query}'. Using generic fallback...")
    # Strategy 3: Try generic fallback
    fallback_query = "technology abstract" if "ai" in query.lower() or "tech" in query.lower() else "nature landscape"
    result = fetch_pexels(fallback_query, orientation)
    if result: return result
        
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

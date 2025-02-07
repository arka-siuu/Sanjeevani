import requests
import re

# Replace with your actual YouTube Data API key
YOUTUBE_API_KEY = "AIzaSyBMZcQRrVzjG-bMaqcUDF1hgz2FI1enTWI"

def extract_keywords(text):
    """
    Extracts relevant keywords from user input.
    """
    stopwords = ["hey", "I", "am", "what", "should", "do", "is", "the", "and", "a", "from", "having"]
    words = re.findall(r'\b[a-zA-Z]+\b', text.lower())
    keywords = [word for word in words if word not in stopwords]
    return " ".join(keywords) if keywords else "health remedies"

def get_youtube_videos(query, num_results=5):
    """
    Fetches YouTube video recommendations using YouTube Data API.
    """
    youtube_url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&q={query}&key={YOUTUBE_API_KEY}&maxResults={num_results}&type=video"

    response = requests.get(youtube_url)

    if response.status_code == 200:
        results = response.json()
        videos = []
        
        for item in results.get("items", []):
            video_id = item["id"]["videoId"]
            video_title = item["snippet"]["title"]
            video_url = f"https://www.youtube.com/watch?v={video_id}"

            videos.append({
                "title": video_title,
                "link": video_url
            })
        
        return videos if videos else [{"title": "No videos found", "link": "#"}]
    
    else:
        return [{"title": f"Error fetching results: {response.status_code}", "link": "#"}]

# Example usage
if __name__ == "__main__":
    user_input = input("Describe your health issue: ")
    
    # Extract keywords from user input
    search_query = extract_keywords(user_input)
    
    # Get YouTube video recommendations
    recommendations = get_youtube_videos(search_query)

    print("\nRecommended Videos:")
    for idx, video in enumerate(recommendations, start=1):
        print(f"{idx}. {video['title']}")
        print(f"   🔗 {video['link']}\n")

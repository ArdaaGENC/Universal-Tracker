import requests
import os
from dotenv import load_dotenv
from core.database import load_timeline

load_dotenv()
OMDB_API_KEY = os.getenv("OMDB_API_KEY")

def get_show_metadata(show_name):
    db = load_timeline()
    for universe, shows in db.items():
        for item in shows:
            if isinstance(item, dict) and item.get("title") == show_name:
                return item.get("type", "show"), item.get("release", "")
            elif isinstance(item, str):
                clean_str = item.replace(" (Film)", "")
                if clean_str == show_name or item == show_name:
                    return "movie" if "(Film)" in item else "show", ""
    return "show", ""

def fetch_show_details(show_name):
    clean_name = show_name.replace(" (Film)", "")
    
    show_type, release_year = get_show_metadata(clean_name)
    is_movie = (show_type == "movie")
    
    if release_year or is_movie:
        omdb_type = "movie" if is_movie else "series"
        result = fetch_from_omdb(clean_name, release_year, omdb_type)
        if result.get("image_url"): return result

    tvmaze_url = f"https://api.tvmaze.com/singlesearch/shows?q={clean_name}"
    try:
        response = requests.get(tvmaze_url)
        if response.status_code == 200:
            data = response.json()
            if data.get("image"):
                return format_tvmaze_data(data)
    except:
        pass

    return fetch_from_omdb(clean_name, "", "movie" if is_movie else "series")

def fetch_from_omdb(show_name, year="", type_filter=""):
    if not OMDB_API_KEY:
        return {"text": "OMDb API key not configured", "image_url": None}
        
    omdb_url = f"http://www.omdbapi.com/?t={show_name}&apikey={OMDB_API_KEY}"
    
    if year:
        omdb_url += f"&y={year}"
    if type_filter:
        omdb_url += f"&type={type_filter}"

    try:
        res = requests.get(omdb_url)
        data = res.json()
        if data.get("Response") == "True":
             rating = data.get("imdbRating", "N/A")
             res_year = data.get("Year", "N/A")
             poster = data.get("Poster", None)
             poster_url = poster if poster != "N/A" else None
             
             type_label = "Movie" if type_filter == "movie" else "Show"

             return{
                "text": f"Rating: {rating}/10 | Year: {res_year} ({type_label})",
                "image_url": poster_url
             }
    except:
        pass
    return {"text": "Show not found", "image_url": None}

def format_tvmaze_data(data):
     rating = data.get("rating", {}).get("average", "N/A")
     premiered = data.get("premiered", "N/A")
     
     year = premiered.split("-")[0] if premiered and premiered != "N/A" else "N/A"
     
     image_url = data["image"].get("medium") if data.get("image") else None
     return {
        "text": f"Rating: {rating}/10 | Year: {year} (Show)",
        "image_url": image_url
     }
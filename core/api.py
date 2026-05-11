import requests
import os
from dotenv import load_dotenv

class APIClient:
    def __init__(self, db_manager):
        load_dotenv()
        self._omdb_api_key = os.getenv("OMDB_API_KEY")
        self._db_manager = db_manager

    def _get_show_metadata(self, show_name):
        db = self._db_manager.load_timeline()
        for universe, shows in db.items():
            for item in shows:
                if isinstance(item, dict) and item.get("title") == show_name:
                    return item.get("type", "show"), item.get("release", "")
                elif isinstance(item, str):
                    clean_str = item.replace(" (Film)", "")
                    if clean_str == show_name or item == show_name:
                        return "movie" if "(Film)" in item else "show", ""
        return "show", ""

    def fetch_show_details(self, show_name):
        clean_name = show_name.replace(" (Film)", "")
        show_type, release_year = self._get_show_metadata(clean_name)
        is_movie = (show_type == "movie")
        
        if release_year or is_movie:
            omdb_type = "movie" if is_movie else "series"
            result = self._fetch_from_omdb(clean_name, release_year, omdb_type)
            if result.get("image_url"): return result

        tvmaze_url = f"https://api.tvmaze.com/singlesearch/shows?q={clean_name}"
        try:
            response = requests.get(tvmaze_url)
            if response.status_code == 200:
                data = response.json()
                if data.get("image"):
                    return self._format_tvmaze_data(data)
        except:
            pass

        return self._fetch_from_omdb(clean_name, "", "movie" if is_movie else "series")

    def _fetch_from_omdb(self, show_name, year="", type_filter=""):
        if not self._omdb_api_key:
            return {"text": "OMDb API key not configured", "image_url": None}
            
        omdb_url = f"http://www.omdbapi.com/?t={show_name}&apikey={self._omdb_api_key}"
        if year: omdb_url += f"&y={year}"
        if type_filter: omdb_url += f"&type={type_filter}"

        try:
            res = requests.get(omdb_url)
            data = res.json()
            if data.get("Response") == "True":
                 return{
                    "text": f"Rating: {data.get('imdbRating', 'N/A')}/10 | Year: {data.get('Year', 'N/A')} ({'Movie' if type_filter == 'movie' else 'Show'})",
                    "image_url": data.get("Poster") if data.get("Poster") != "N/A" else None
                 }
        except:
            pass
        return {"text": "Show not found", "image_url": None}

    def _format_tvmaze_data(self, data):
         premiered = data.get("premiered", "N/A")
         year = premiered.split("-")[0] if premiered and premiered != "N/A" else "N/A"
         return {
            "text": f"Rating: {data.get('rating', {}).get('average', 'N/A')}/10 | Year: {year} (Show)",
            "image_url": data["image"].get("medium") if data.get("image") else None
         }
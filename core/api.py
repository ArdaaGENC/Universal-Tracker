import requests
import os
import json
import re
from dotenv import load_dotenv

class APIClient:
    def __init__(self, db_manager):
        load_dotenv()
        self._tmdb_api_key = os.getenv("TMDB_API_KEY")
        self._omdb_api_key = os.getenv("OMDB_API_KEY")
        self._db_manager = db_manager
        
        self._cache = {}
        self._cache_file = os.path.join("data", "api_cache.json")
        self._posters_dir = os.path.join("data", "posters")
        os.makedirs(self._posters_dir, exist_ok=True)
        self._persistent_cache = self._load_cache()

    def _load_cache(self):
        if os.path.exists(self._cache_file):
            try:
                with open(self._cache_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except: pass
        return {}
    
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
        if show_name in self._cache and self._cache[show_name].get("image_url"):
            return self._cache[show_name]

        if show_name in self._persistent_cache:
            data = self._persistent_cache[show_name]
            if data.get("image_url"):
                self._cache[show_name] = data
                return data

        clean_name = show_name.replace(" (Film)", "")
        
        show_type, release_year = self._get_show_metadata(clean_name)
        is_movie = (show_type == "movie")
        
        result = self._fetch_from_tmdb(clean_name, is_movie, release_year)
        
        if not result or not result.get("image_url"):
            omdb_type = "movie" if is_movie else "series"
            result = self._fetch_from_omdb(clean_name, release_year, omdb_type)

        if not result:
            result = {"text": "Not found", "image_url": None, "local_image_path": None}

        if result.get("image_url") and not result.get("local_image_path"):
            result = self._download_poster(clean_name, result)

        self._cache[show_name] = result
        self._persistent_cache[show_name] = result
        self._save_cache()
        return result

    def _fetch_from_tmdb(self, name, is_movie=False, year=""):
        if not self._tmdb_api_key: return None
        
        search_type = "movie" if is_movie else "multi"
        url = f"https://api.themoviedb.org/3/search/{search_type}?api_key={self._tmdb_api_key}&query={name}"
        
        if year and is_movie:
            url += f"&primary_release_year={year}"
        elif year and not is_movie:
            url += f"&first_air_date_year={year}"

        try:
            res = requests.get(url).json()
            if res.get("results"):
                item = res["results"][0]
                poster_path = item.get("poster_path")
                m_type = item.get("media_type", search_type) 
                return {
                    "tmdb_id": item.get("id"),
                    "media_type": m_type,
                    "text": f"Rating: {item.get('vote_average', 'N/A')}/10",
                    "image_url": f"https://image.tmdb.org/t/p/w500{poster_path}" if poster_path else None
                }
        except: pass
        return None

    def get_recommendations(self, tmdb_id, media_type="movie"):
        if not tmdb_id or not self._tmdb_api_key: return []
        url = f"https://api.themoviedb.org/3/{media_type}/{tmdb_id}/recommendations?api_key={self._tmdb_api_key}"
        try:
            res = requests.get(url).json()
            recs = []
            for item in res.get("results", [])[:5]:
                recs.append({
                    "title": item.get("title") or item.get("name"),
                    "image": f"https://image.tmdb.org/t/p/w200{item.get('poster_path')}" if item.get("poster_path") else None,
                    "type": item.get("media_type", media_type)
                })
            return recs
        except: return []

    def _download_poster(self, name, result):
        safe_name = re.sub(r'[\\/*?:"<>|]', "", name)
        local_path = os.path.join(self._posters_dir, f"{safe_name}.jpg")
        try:
            img_data = requests.get(result["image_url"]).content
            with open(local_path, 'wb') as f:
                f.write(img_data)
            result["local_image_path"] = local_path
        except: pass
        return result

    def _save_cache(self):
        with open(self._cache_file, "w", encoding="utf-8") as f:
            json.dump(self._persistent_cache, f, indent=4)
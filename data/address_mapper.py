import json
import os
from pathlib import Path
from config import CACHE_FILE, ENABLE_CACHE

class AddressMapper:
    '''Manages address to physical_id mapping with caching'''
    
    def __init__(self):
        self.cache = self._load_cache()
    
    def _load_cache(self):
        '''Load cached address mappings'''
        if not ENABLE_CACHE:
            return {}
        
        try:
            if os.path.exists(CACHE_FILE):
                with open(CACHE_FILE, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading cache: {e}")
        
        return {}
    
    def _save_cache(self):
        '''Save cache to file'''
        if not ENABLE_CACHE:
            return
        
        try:
            # Create cache directory if it doesn't exist
            Path(CACHE_FILE).parent.mkdir(parents=True, exist_ok=True)
            
            with open(CACHE_FILE, 'w') as f:
                json.dump(self.cache, f, indent=2)
        except Exception as e:
            print(f"Error saving cache: {e}")
    
    def _make_cache_key(self, street_name, house_number, borough_code=None):
        '''Create cache key from address components'''
        return f"{house_number}_{street_name.upper()}_{borough_code or ''}"
    
    def get_cached_physical_id(self, street_name, house_number, borough_code=None):
        '''Look up physical_id from cache'''
        key = self._make_cache_key(street_name, house_number, borough_code)
        return self.cache.get(key)
    
    def cache_physical_id(self, street_name, house_number, physical_id, borough_code=None):
        '''Store physical_id in cache'''
        key = self._make_cache_key(street_name, house_number, borough_code)
        self.cache[key] = physical_id
        self._save_cache()
    
    def clear_cache(self):
        '''Clear all cached mappings'''
        self.cache = {}
        self._save_cache()
import requests


class Nominatim:
    def __init__(self):
        self.base_url = "https://nominatim.openstreetmap.org/search"

    def query(self, query: str, limit=1):
        headers = {'User-Agent': 'YourAppName/1.0'}
        response = requests.get(self.base_url, params={
            'format': 'json',
            'addressdetails': 1,
            'limit': limit,
            'q': query
        }, headers=headers)

        # Check for a successful response
        response.raise_for_status()  # Raise an error for bad responses
        return response.json()

    def get_location_details(self, query: str):
        if query is None or len(query) == 0:
            return None
        results = self.query(query)
        if results:
            return results[0]
        return None

    def get_location_full_name(self, query: str):
        if query is None or len(query) == 0:
            return None
        results = self.query(query)
        if results:
            return results[0]["display_name"]
        return None

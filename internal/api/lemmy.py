import requests

class LemmyScraper:
    def __init__(self):
        self.base_url = 'https://lemmy.world/api/v3'
        
    def get_latest_posts(self, limit=1, sort='New'):
        url = self.base_url + '/post/list'
        params = {
            'community_name': 'unixporn',
            'limit': limit,
            'sort': sort
        }

        try:
            response = requests.get(url, params=params)
            data = response.json()
            posts = data.get('posts', [])
            return posts[0]['post']

        except requests.RequestException as e:
            print(f"[get_latest_posts] Error fetching posts: {e}")
            return None

import os, requests
from common.logger import log

def dir_exist(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)


def download_media(url, filename):
  headers = {
      "User-Agent": "Mozilla/5.0"
  }
  try:
      response = requests.get(url, headers=headers, stream=True, allow_redirects=True)
      response.raise_for_status()
      with open(filename, 'wb') as f:
          for chunk in response.iter_content(1024):
              f.write(chunk)
      log.info(f"[download_media] Image saved to {filename}")
  except requests.RequestException as e:
      log.error(f"[download_media] Error downloading media: {e}")
      return None
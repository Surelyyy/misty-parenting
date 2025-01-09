import requests
from PIL import Image
import io

url = "http://192.168.0.149/api/cameras/rgb"
try:
    response = requests.get(url, timeout=5, stream=True)
    if response.status_code == 200:
        print("Connection Successful!")
        image = Image.open(io.BytesIO(response.content))
        image.show()  # Opens the image in the default viewer
    else:
        print(f"Failed to connect. Status code: {response.status_code}")
except requests.exceptions.RequestException as e:
    print(f"Connection error: {e}")

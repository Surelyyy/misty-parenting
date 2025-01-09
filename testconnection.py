# testConnect.py
import requests
from PIL import Image
import io

def test_connection(ip_address):
    """Test connection to Misty's camera."""
    url = f"http://{ip_address}/api/cameras/rgb"
    try:
        response = requests.get(url, timeout=5, stream=True)
        if response.status_code == 200:
            # Return the image content if successful
            return {"success": True, "image_data": response.content}
        else:
            return {"success": False, "error": f"HTTP Error {response.status_code}"}
    except requests.exceptions.RequestException as e:
        return {"success": False, "error": str(e)}

# Only execute if run directly (for standalone testing)
if __name__ == "__main__":
    ip_address = input("Enter Misty II's IP address: ")
    result = test_connection(ip_address)
    if result["success"]:
        print("Connection successful! Displaying image...")
        image = Image.open(io.BytesIO(result["image_data"]))
        image.show()
    else:
        print(f"Connection failed: {result['error']}")

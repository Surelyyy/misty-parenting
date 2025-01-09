
def test_connection(ip_address):
    """Test connection to Misty's camera."""
    url = f"http://{ip_address}/api/cameras/rgb"
    try:
        response = requests.get(url, timeout=5, stream=True)
        if response.status_code == 200:
            # Save the image to a temporary file
            temp_image_path = "misty_temp_image.jpg"
            with open(temp_image_path, "wb") as f:
                f.write(response.content)
            return {"success": True, "temp_image_path": temp_image_path}
        else:
            return {"success": False, "error": f"HTTP Error {response.status_code}"}
    except requests.exceptions.RequestException as e:
        return {"success": False, "error": str(e)}

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python testConnect.py <ip_address>")
        sys.exit(1)

    ip_address = sys.argv[1]
    result = test_connection(ip_address)
    if result["success"]:
        print("Connection successful!")
    else:
        print(f"Connection failed: {result['error']}")

import streamlit as st
import requests
from PIL import Image
import io

# Streamlit App Title
st.title("Misty II Camera Connection Test")

# Input for Misty's IP Address
ip_address = st.text_input("Enter Misty II's IP address:", placeholder="192.168.x.x")

# Button to Test Connection
if st.button("Test Connection"):
    # Construct the URL for Misty's camera API
    url = f"http://{ip_address}/api/cameras/rgb"
    
    # Try to fetch the image
    try:
        response = requests.get(url, timeout=5, stream=True)
        
        # Check if the response is successful and contains image data
        if response.status_code == 200:
            # Load the image from the response content
            image = Image.open(io.BytesIO(response.content))
            st.success("Successfully connected to Misty! Here's the image captured:")
            st.image(image, caption="Image from Misty's Camera", use_column_width=True)
        else:
            st.error(f"Failed to connect. Status code: {response.status_code}")
    except requests.exceptions.RequestException as e:
        st.error(f"Connection error: {e}")

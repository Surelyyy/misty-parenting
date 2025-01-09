# Streamlit App for Misty II Real-Time Vision and Number Recognition
import streamlit as st
import requests
import numpy as np
import tensorflow.lite as tflite
from PIL import Image
import io
import time

# Define Misty's API endpoint for capturing an image
def capture_image(ip_address):
    """Capture an image from Misty's camera."""
    url = f"http://{ip_address}/api/cameras/rgb"  # Use HTTP, port 80
    try:
        response = requests.get(url, timeout=5, stream=True)
        if response.status_code == 200:
            return response.content  # Return binary image data
        return None
    except requests.exceptions.RequestException as e:
        st.error(f"Failed to capture image: {e}")
        return None



# Initialize Streamlit App
st.title("Misty II Real-Time Vision and Number Recognition")

# Initialize session state
if "connected" not in st.session_state:
    st.session_state["connected"] = False
if "ip_address" not in st.session_state:
    st.session_state["ip_address"] = ""

# Connect to Misty using camera test
if not st.session_state["connected"]:
    ip_address = st.text_input("Enter Misty II's IP address:", placeholder="192.168.x.x", key="ip_input")

    if st.button("Connect", key="connect_button"):
        image_data = capture_image(ip_address)
        if image_data:
            st.success("Successfully connected to Misty! Camera is working.")
            st.session_state["connected"] = True
            st.session_state["ip_address"] = ip_address
            # Display a sample frame to confirm connection
            image = Image.open(io.BytesIO(image_data))
            st.image(image, caption="Sample Image from Misty", use_column_width=True)
        else:
            st.error("Failed to connect to Misty. Ensure the IP address and camera API are correct.")


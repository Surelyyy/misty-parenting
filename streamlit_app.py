import logging
import streamlit as st
import requests
import numpy as np
import tensorflow.lite as tflite
from PIL import Image
import io
import time

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,  # Adjust the level as needed
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

# Define Misty's API endpoints
def misty_speak(ip_address, text):
    """Make Misty speak a text."""
    url = f"http://{ip_address}/api/tts/speak"
    payload = {"text": text}
    try:
        logging.debug(f"Sending TTS request to Misty at {url} with payload: {payload}")
        response = requests.post(url, json=payload, timeout=5)
        if response.status_code == 200:
            logging.info("Misty spoke successfully.")
        else:
            logging.error(f"TTS request failed with status code: {response.status_code}")
        return response.status_code == 200
    except requests.exceptions.RequestException as e:
        logging.error(f"Error during TTS request: {e}")
        return False

def capture_image(ip_address):
    """Capture an image from Misty's camera."""
    url = f"http://{ip_address}/api/cameras/rgb"
    try:
        logging.debug(f"Requesting image from Misty at {url}")
        response = requests.get(url, timeout=5, stream=True)
        if response.status_code == 200:
            logging.info("Image captured successfully.")
            return response.content  # Binary image data
        logging.error(f"Image capture failed with status code: {response.status_code}")
        return None
    except requests.exceptions.RequestException as e:
        logging.error(f"Error during image capture request: {e}")
        return None

def test_connection(ip_address):
    """Test connection to Misty."""
    url = f"http://{ip_address}/api/device"
    try:
        logging.debug(f"Testing connection to Misty at {url}")
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            logging.info("Connection to Misty is successful.")
        else:
            logging.warning(f"Connection test returned status code: {response.status_code}")
        return response.status_code == 200
    except requests.exceptions.RequestException as e:
        logging.error(f"Error during connection test: {e}")
        return False

# Streamlit application
st.title("Misty II Debugging and Learning Module")

# Connection handling
ip_address = st.text_input("Enter Misty II's IP address:", placeholder="192.168.x.x")
if st.button("Connect"):
    if test_connection(ip_address):
        st.success("Connection to Misty is successful!")
        st.session_state["connected"] = True
        logging.info(f"Successfully connected to Misty at {ip_address}")
    else:
        st.error("Failed to connect to Misty. Check the IP address.")
        logging.warning(f"Failed connection attempt to Misty at {ip_address}")

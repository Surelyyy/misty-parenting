# Streamlit App for Misty II Real-Time Vision and Number Recognition
import streamlit as st
import requests
import numpy as np
import tensorflow.lite as tflite
from PIL import Image
import io
import time

import requests

ip_address = "192.168.0.149"
url = f"http://{ip_address}/api/cameras/rgb"
try:
    response = requests.get(url, timeout=5)
    if response.status_code == 200:
        print("Connection successful!")
    else:
        print(f"Unexpected status code: {response.status_code}")
except requests.exceptions.RequestException as e:
    print(f"Connection error: {e}")


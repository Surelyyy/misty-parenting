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
url = f"http://192.168.0.149/api/videos?base64=false"
try:
    response = requests.get(url, timeout=5)
    if response.status_code == 200:
        st.error("Connection successful!")
    else:
        st.error(f"Unexpected status code: {response.status_code}")
except requests.exceptions.RequestException as e:
    st.error(f"Connection error: {e}")


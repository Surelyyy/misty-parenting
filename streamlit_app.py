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
    url = f"https://{ip_address}:443/api/cameras/rgb"
    try:
        st.write(f"Attempting to connect to Misty's camera at {url}")
        response = requests.get(url, timeout=5, stream=True, verify = False)
        st.write(f"Response Code: {response.status_code}")
        if response.status_code == 200:
            return response.content  # Binary image data
        st.write(f"Failed with Response: {response.text}")
        return None
    except requests.exceptions.RequestException as e:
        st.error(f"Connection error: {e}")
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

# Real-Time Prediction and Vision
if st.session_state.get("connected"):
    st.subheader(f"Connected to Misty II at {st.session_state['ip_address']}")

    # Load TFLite model
    model_path = "number_recognition_ming.tflite"  # Update with your model's path
    tflite_model = None
    try:
        interpreter = tflite.Interpreter(model_path=model_path)
        interpreter.allocate_tensors()
        tflite_model = interpreter
        st.success("TFLite model loaded successfully!")
    except Exception as e:
        st.error(f"Failed to load model: {e}")

    if tflite_model is not None:
        st.header("Live Vision and Number Recognition")

        # Placeholders for dynamic updates
        frame_placeholder = st.empty()
        prediction_placeholder = st.empty()

        # Start real-time capture and prediction
        if st.button("Start Real-Time Recognition"):
            try:
                random_number = np.random.randint(1, 10)
                st.write(f"Show me the number {random_number}!")

                # Process frames continuously
                while True:
                    start_time = time.time()
                    image_data = capture_image(st.session_state["ip_address"])
                    if image_data:
                        # Display captured image
                        image = Image.open(io.BytesIO(image_data))
                        frame_placeholder.image(image, caption="Misty's Vision", use_column_width=True)

                        # Preprocess image and predict (implement preprocessing and prediction logic here)
                        # processed_image = preprocess_image(image)
                        # predicted_number, confidence = predict_number(tflite_model, processed_image)
                        # Replace above lines with appropriate logic for your model

                    else:
                        st.error("Failed to capture image. Ensure Misty's camera is functioning.")

                    # Maintain 10 FPS
                    elapsed_time = time.time() - start_time
                    time.sleep(max(0, 0.1 - elapsed_time))  # Adjust delay for 10 FPS
            except Exception as e:
                st.error(f"An error occurred: {e}")

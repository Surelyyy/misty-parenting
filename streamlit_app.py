import streamlit as st
import requests
import numpy as np
import tensorflow.lite as tflite
import time
from PIL import Image
import io

# Define a function to test connection with Misty II
def test_connection(ip_address):
    try:
        response = requests.get(f"http://{ip_address}/api/device", timeout=5)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False

# Define Misty's API endpoints
def misty_speak(ip_address, text):
    """Make Misty speak a text."""
    url = f"http://{ip_address}/api/tts/speak"
    payload = {"text": text}
    try:
        response = requests.post(url, json=payload, timeout=5)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False

def capture_image(ip_address):
    """Capture an image from Misty's camera."""
    url = f"http://{ip_address}/api/cameras/rgb"
    try:
        response = requests.get(url, timeout=5, stream=True)
        if response.status_code == 200:
            return response.content  # Binary image data
        return None
    except requests.exceptions.RequestException:
        return None

def load_tflite_model(model_path):
    """Load TFLite model."""
    try:
        interpreter = tflite.Interpreter(model_path=model_path)
        interpreter.allocate_tensors()
        return interpreter
    except Exception as e:
        st.error(f"Failed to load model: {e}")
        return None

def predict_number(interpreter, image_data):
    """Predict number using TFLite model."""
    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()

    interpreter.set_tensor(input_details[0]['index'], image_data)
    interpreter.invoke()
    output_data = interpreter.get_tensor(output_details[0]['index'])
    return np.argmax(output_data)

# Initialize Streamlit App
st.title("Misty II Learning Module")

# Initialize session state
if "connected" not in st.session_state:
    st.session_state["connected"] = False
if "ip_address" not in st.session_state:
    st.session_state["ip_address"] = ""

# Connect to Misty
if not st.session_state["connected"]:
    ip_address = st.text_input("Enter Misty II's IP address:", placeholder="192.168.x.x", key="ip_input")

    if st.button("Connect", key="connect_button"):
        if misty_speak(ip_address, "Connection successful!"):
            st.success("Misty is connected!")
            st.session_state["connected"] = True
            st.session_state["ip_address"] = ip_address
        else:
            st.error("Failed to connect to Misty. Check the IP address.")

# Learning Module
if st.session_state.get("connected"):
    st.subheader(f"Connected to Misty II at {st.session_state['ip_address']}")

    # Load TFLite model
    model_path = "number_recognition_ming.tflite"  # Update with your model's path
    tflite_model = load_tflite_model(model_path)

    if tflite_model is not None:
        # Level 1: Number Recognition
        st.header("Learning Module: Level 1 - Number Recognition")
        random_number = np.random.randint(1, 10)
        text_instruction = f"Can you show me number {random_number}?"
        misty_speak(st.session_state["ip_address"], text_instruction)

        st.write(text_instruction)

        # Real-Time Image Capture and Prediction
        if st.button("Capture Image", key="capture_button"):
            image_data = capture_image(st.session_state["ip_address"])
            if image_data:
                # Display captured image
                image = Image.open(io.BytesIO(image_data))
                st.image(image, caption="Captured Image from Misty", use_column_width=True)

                # Preprocess image for TFLite model
            
                # Replace this with the actual preprocessing logic for your model
                processed_image = np.array(image.resize((28, 28)).convert("L")) / 255.0
                processed_image = processed_image.reshape(1, 28, 28, 1).astype(np.float32)

                predicted_number = predict_number(tflite_model, processed_image)
                st.write(f"Misty recognized the number: {predicted_number}")

                if predicted_number == random_number:
                    st.success("Correct! Moving to Level 2.")
                    # Implement Level 2 here
                else:
                    st.error("Incorrect. Try again!")
            else:
                st.error("Failed to capture image. Ensure Misty's camera is functioning.")

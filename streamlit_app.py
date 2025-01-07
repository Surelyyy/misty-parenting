import streamlit as st
import requests
import numpy as np
import tensorflow.lite as tflite
from PIL import Image
import io
import time

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

def preprocess_image(image):
    """Preprocess the image for TFLite model."""
    resized_image = image.resize((28, 28)).convert("L")  # Resize and convert to grayscale
    normalized_image = np.array(resized_image) / 255.0  # Normalize pixel values
    reshaped_image = normalized_image.reshape(1, 28, 28, 1).astype(np.float32)  # Add batch dimension
    return reshaped_image

def predict_number(interpreter, image_data):
    """Predict number using TFLite model."""
    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()

    interpreter.set_tensor(input_details[0]['index'], image_data)
    interpreter.invoke()
    output_data = interpreter.get_tensor(output_details[0]['index'])
    return np.argmax(output_data)

# Initialize Streamlit App
st.title("Misty II Real-Time Number Recognition")

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

# Real-Time Prediction
if st.session_state.get("connected"):
    st.subheader(f"Connected to Misty II at {st.session_state['ip_address']}")

    # Load TFLite model
    model_path = "number_recognition_ming.tflite"  # Update with your model's path
    tflite_model = load_tflite_model(model_path)

    if tflite_model is not None:
        st.header("Real-Time Number Recognition")

        # Placeholder for dynamic updates
        result_placeholder = st.empty()
        frame_placeholder = st.empty()

        # Start real-time capture and prediction
        if st.button("Start Real-Time Recognition"):
            try:
                random_number = np.random.randint(1, 10)
                text_instruction = f"Can you show me number {random_number}?"
                misty_speak(st.session_state["ip_address"], text_instruction)
                st.write(text_instruction)

                # Process frames at 10 FPS
                while True:
                    start_time = time.time()
                    image_data = capture_image(st.session_state["ip_address"])
                    if image_data:
                        # Display captured image
                        image = Image.open(io.BytesIO(image_data))
                        frame_placeholder.image(image, caption="Captured Image", use_column_width=True)

                        # Preprocess image and predict
                        processed_image = preprocess_image(image)
                        predicted_number = predict_number(tflite_model, processed_image)
                        result_placeholder.write(f"Misty recognized the number: {predicted_number}")

                        if predicted_number == random_number:
                            result_placeholder.success("Correct! Moving to the next number.")
                            random_number = np.random.randint(1, 10)
                            text_instruction = f"Can you show me number {random_number}?"
                            misty_speak(st.session_state["ip_address"], text_instruction)
                            st.write(text_instruction)

                    # Maintain 10 FPS
                    elapsed_time = time.time() - start_time
                    time.sleep(max(0, 0.1 - elapsed_time))  # Adjust delay for 10 FPS
            except Exception as e:
                st.error(f"An error occurred: {e}")

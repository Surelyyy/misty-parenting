import streamlit as st
import requests
import numpy as np
import tensorflow.lite as tflite
from PIL import Image
import io
import time

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
    """Predict number using TFLite model with confidence filtering."""
    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()

    # Set input tensor and invoke the interpreter
    interpreter.set_tensor(input_details[0]['index'], image_data)
    interpreter.invoke()
    output_data = interpreter.get_tensor(output_details[0]['index'])  # Confidence scores for each class

    # Find the class with the highest confidence
    max_confidence = np.max(output_data)
    predicted_class = np.argmax(output_data)

    # Filter by confidence level (80%)
    if max_confidence >= 0.8:
        return predicted_class, max_confidence
    else:
        return None, max_confidence


# Initialize Streamlit App
st.title("Misty II Real-Time Vision and Number Recognition")

# Initialize session state
if "connected" not in st.session_state:
    st.session_state["connected"] = False
if "ip_address" not in st.session_state:
    st.session_state["ip_address"] = ""

# Define a function to test the connection to Misty using the root URL
def test_connection(ip_address):
    """Test connection to Misty's base URL."""
    url = f"http://{ip_address}/"
    try:
        logging.debug(f"Testing connection to Misty at {url}")
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            logging.info("Successfully connected to Misty.")
            return True
        else:
            logging.warning(f"Connection test returned status code: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        logging.error(f"Error during connection test: {e}")
        return False

# Connect to Misty
if not st.session_state["connected"]:
    ip_address = st.text_input("Enter Misty II's IP address:", placeholder="192.168.x.x", key="ip_input")

    if st.button("Connect", key="connect_button"):
        if test_connection(ip_address):
            # Misty is reachable; now confirm with a spoken message
            if misty_speak(ip_address, "Connection successful!"):
                st.success("Misty is connected!")
                st.session_state["connected"] = True
                st.session_state["ip_address"] = ip_address
            else:
                st.error("Misty is reachable but failed to respond to the speak command.")
        else:
            st.error("Failed to connect to Misty. Check the IP address or network settings.")

# Real-Time Prediction and Vision
if st.session_state.get("connected"):
    st.subheader(f"Connected to Misty II at {st.session_state['ip_address']}")

    # Load TFLite model
    model_path = "number_recognition_ming.tflite"  # Update with your model's path
    tflite_model = load_tflite_model(model_path)

    if tflite_model is not None:
        st.header("Live Vision and Number Recognition")

        # Placeholders for dynamic updates
        frame_placeholder = st.empty()
        prediction_placeholder = st.empty()

        # Start real-time capture and prediction
        if st.button("Start Real-Time Recognition"):
            try:
                random_number = np.random.randint(1, 10)
                text_instruction = f"Can you show me number {random_number}?"
                misty_speak(st.session_state["ip_address"], text_instruction)
                st.write(text_instruction)
        
                # Process frames continuously
                while True:
                    start_time = time.time()
                    image_data = capture_image(st.session_state["ip_address"])
                    if image_data:
                        # Display captured image
                        image = Image.open(io.BytesIO(image_data))
                        frame_placeholder.image(image, caption="Misty's Vision", use_column_width=True)
        
                        # Preprocess image and predict
                        processed_image = preprocess_image(image)
                        predicted_number, confidence = predict_number_with_confidence(tflite_model, processed_image)
        
                        if predicted_number is not None:
                            prediction_placeholder.subheader(f"Prediction: {predicted_number} (Confidence: {confidence:.2f})")
        
                            if predicted_number == random_number:
                                prediction_placeholder.success("Correct! Moving to the next number.")
                                random_number = np.random.randint(1, 10)
                                text_instruction = f"Can you show me number {random_number}?"
                                misty_speak(st.session_state["ip_address"], text_instruction)
                                st.write(text_instruction)
                        else:
                            prediction_placeholder.error("Can't recognize number. Confidence is too low.")
                    else:
                        st.error("Failed to capture image. Ensure Misty's camera is functioning.")
        
                    # Maintain 10 FPS
                    elapsed_time = time.time() - start_time
                    time.sleep(max(0, 0.1 - elapsed_time))  # Adjust delay for 10 FPS
            except Exception as e:
                st.error(f"An error occurred: {e}")
        

import streamlit as st
import requests
import logging
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

# Define a function to test the connection to Misty using the root URL
def test_connection(ip_address):
    """Test connection to Misty's device API."""
    url = f"http://{ip_address}/api/device"
    try:
        logging.debug(f"Testing connection to Misty at {url}")
        response = requests.get(url, timeout=10)  # Increased timeout to 10 seconds
        logging.debug(f"Response Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            logging.debug(f"Response JSON: {data}")
            if data.get("status") == "Success":
                logging.info("Successfully connected to Misty.")
                return True
            else:
                logging.warning("Misty responded, but status is not 'Success'.")
                return False
        else:
            logging.warning(f"Connection test returned status code: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        logging.error(f"RequestException: {e}")
        return False


# Initialize Streamlit App
st.title("Misty II Real-Time Vision and Number Recognition")

# Initialize session state
if "connected" not in st.session_state:
    st.session_state["connected"] = False
if "ip_address" not in st.session_state:
    st.session_state["ip_address"] = ""

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

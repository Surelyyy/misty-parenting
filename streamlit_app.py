# Streamlit App
import streamlit as st
import subprocess
import json
from PIL import Image
import io
import os

# Streamlit Title
st.title("Misty II Connection Tester")

# Get IP address from user
ip_address = st.text_input("Enter Misty II's IP address:", placeholder="192.168.x.x")

if st.button("Test Connection"):
    if ip_address:
        try:
            # Run the `testconnection.py` script with the IP address as an argument
            result = subprocess.run(
                ["python", "testConnect.py", ip_address],
                capture_output=True,
                text=True,
                check=True
            )
            
            # Extract the output from the subprocess
            output = result.stdout.strip()
            
            # Handle the output and display results
            if "Connection successful!" in output:
                st.success("Successfully connected to Misty!")
                
                # Assuming the script saves the image to a temporary file
                image_path = "misty_temp_image.jpg"  # Update based on `testConnect.py` behavior
                if os.path.exists(image_path):
                    image = Image.open(image_path)
                    st.image(image, caption="Misty's Camera Output", use_column_width=True)
                    os.remove(image_path)  # Clean up after displaying the image
                else:
                    st.warning("Image file not found. Connection may still be successful.")
            else:
                st.error(f"Connection failed: {output}")
        
        except subprocess.CalledProcessError as e:
            st.error(f"Error testing connection: {e.stderr.strip()}")
    else:
        st.warning("Please enter a valid IP address.")

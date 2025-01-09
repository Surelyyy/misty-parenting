# Streamlit App
import streamlit as st
import subprocess
import json
from PIL import Image
import io

# Streamlit Title
st.title("Misty II Connection Tester")

# Get IP address from user
ip_address = st.text_input("Enter Misty II's IP address:", placeholder="192.168.x.x")

if st.button("Test Connection"):
    if ip_address:
        try:
            # Run the `testConnect.py` script with the IP address as an argument
            result = subprocess.run(
                ["python", "testconnection.py", ip_address],
                capture_output=True,
                text=True,
                check=True
            )
            
            # Parse the output from the script
            output = result.stdout.strip()
            
            if "Connection successful!" in output:
                # Extract and display the image (simulate returning from testConnect)
                # Assuming the script would save the image to a temporary file for simplicity
                st.success("Successfully connected to Misty!")
                image_data = output.split("DATA:")[1]  # Assuming testConnect returns "DATA:<binary>"
                image = Image.open(io.BytesIO(image_data)) # Use PIL patch/PST
                st.image(image, caption='MISTY:', caption=""></ANIM now 

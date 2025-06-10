#!/bin/bash

# Install Python packages
pip install -r requirements.txt

# Start the Streamlit app
streamlit run app.py --server.port $PORT --server.enableCORS false

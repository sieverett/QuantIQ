#!/bin/bash

# Make sure setup.sh is executable
chmod +x setup.sh

# This script installs wkhtmltopdf
./setup.sh

python -m streamlit run quantiq.py --server.port 8000 --server.address 0.0.0.0
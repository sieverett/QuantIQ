#!/bin/bash

# Make sure setup.sh is executable
sudo apt update
sudo apt install -y wkhtmltopdf

python -m streamlit run quantiq.py --server.port 8000 --server.address 0.0.0.0
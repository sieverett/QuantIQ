#!/bin/bash

# Make sure wkhtmltopdf is setup
apt update
apt install -y wkhtmltopdf
export PATH='$PATH:/usr/bin/wkhtmltopdf'

python -m streamlit run quantiq.py --server.port 8000 --server.address 0.0.0.0
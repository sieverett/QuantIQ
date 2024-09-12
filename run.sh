#!/bin/bash

# Make sure wkhtmltopdf is setup
sudo apt update
sudo apt install -y wkhtmltopdf
echo 'export PATH=$PATH:/usr/local/bin/wkhtmltopdf' >> ~/.bashrc
source ~/.bashrc

python -m streamlit run quantiq.py --server.port 8000 --server.address 0.0.0.0
#!/bin/bash
python -m streamlit run quantiq.py --server.port 8000 --server.address 0.0.0.0

# Make sure setup.sh is executable
chmod +x setup.sh

# Run the setup.sh file
./setup.sh
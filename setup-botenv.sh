#!/bin/bash

# Create venv
python3 -m venv .botenv

# Activate venv
source .botenv/bin/activate

# Install the reguirements
pip3 install -r requirements.txt
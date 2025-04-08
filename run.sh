#!/bin/bash

echo "> Starting application processes..."

# start each process in a new window
gnome-terminal -- bash -c "uvicorn app.main:app --reload; exec bash" &
gnome-terminal -- bash -c "streamlit run ui.py; exec bash" &
@echo off
echo > Starting processes...
echo uvicorn app.main:app --reload
start "Uvicorn Server" cmd /k "uvicorn app.main:app --reload"
echo streamlit run ui.py
start "Streamlit UI" cmd /k "streamlit run ui.py"
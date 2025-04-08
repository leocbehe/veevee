# processes to run
$uvicornProcess = "uvicorn app.main:app --reload"
$streamlitProcess = "streamlit run ui.py"

Write-Host "> Starting application processes..."

# start each process in a new window
Write-Host $uvicorn_process
Start-Process powershell -ArgumentList "-NoExit", "-Command", $uvicornProcess -WindowStyle Normal 
Write-Host $streamlit_process
Start-Process powershell -ArgumentList "-NoExit", "-Command", $streamlitProcess -WindowStyle Normal
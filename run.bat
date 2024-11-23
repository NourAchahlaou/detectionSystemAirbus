@echo off
echo Starting backend...

REM Navigate to the backend directory relative to the script's location
cd backend
start cmd /k "uvicorn main:app --reload" 

echo Starting frontend...

REM Navigate to the frontend directory relative to the script's location
cd ../frontend/defect_detection_system
start cmd /k "npm start"

pause

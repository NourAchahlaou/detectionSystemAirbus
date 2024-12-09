# Real-Time Piece Inspection and Detection System

## Project Overview

This project is designed to provide real-time inspection and detection of industrial pieces in a manufacturing lot. The system ensures that pieces belong to the specified lot type and identifies them based on their unique reference labels (e.g., `D123.4567`). The system uses **YOLOv8** for object detection, which is trained to differentiate between similar and distinct pieces, making the process of verifying lot types more efficient and accurate.

### Key Features:
- **Real-time inspection**: Detects pieces as they pass through the system.
- **Lot type verification**: Identifies pieces that do not belong to the specified lot type.
- **Piece identification**: Identifies pieces using their unique reference labels.
- **Database integration**: Stores piece data and inspection logs in a PostgreSQL database.
- **Admin and user login**: Provides role-based access for system users.
- **Customizable settings**: Allows management of piece references and lot types.

## Technologies Used

This system uses the following technologies:
- **YOLOv8**: For object detection and classification.
- **Flask** and **FastAPI**: For backend development and API handling.
- **React**: For building the interactive frontend.
- **PostgreSQL**: For database management.
- **OpenCV**: For camera integration and image processing.
- **TensorFlow**: For machine learning and model training.

## Setup Instructions

### Prerequisites

Before setting up the project, make sure you have the following installed:

- **Python 3.x**
- **Node.js** and **npm**
- **PostgreSQL**

### Backend Setup

1. Clone the repository:
```bash
   git clone https://github.com/NourAchahlaou/detectionSystemAirbus
   cd detectionSystemAirbus/backend
```   

2. Install Python dependencies:
```bash
    pip install -r requirements.txt
```   
### Frontend Setup

1. Navigate to the frontend directory:
```bash
    cd detectionSystemAirbus/frontend/detection_system

```


2. Install npm dependencies:
```bash
    npm install
```   
### Running the Application
You can run the application using either of the following methods:

    #### Methode 1 :Manual Start

1. Open a PowerShell window for the frontend:

```bash
    cd frontend\detection_system
    npm start
```  
2. Open another PowerShell window for the backend:

```bash
    cd backend
    uvicorn main:app --reload
```  
    #### Methode 2 : Using run.bat
    
Alternatively, you can simply double-click the run.bat file in the project root to automatically start both the frontend and backend servers. 

## Default Login Credentials
Username: admin
Password: admin123

## Database Configuration
Database Name: defectdetectiondb
User: postgres
Password: admin



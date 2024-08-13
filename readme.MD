# NST-Webapp

A fullstack web application to transfer style and content of two images

## Overview

This project consists of two main parts: the frontend and the backend. The frontend is a React application that allows users to upload images for neural style transfer. The backend is a FastAPI application that handles the image processing using a neural style transfer model.

## Prerequisites

- Node.js (for the frontend)
- Python 3.7+ (for the backend)
- pip (Python package installer)

## Frontend

### Installation

1. Navigate to the `frontend` directory:
    ```sh
    cd frontend
    ```

2. Install the dependencies:
    ```sh
    npm install
    ```

### Running the Frontend

1. Start the development server:
    ```sh
    npm start
    ```

2. Open your browser and navigate to `http://localhost:3000`.

### File Structure

- `src/components/ImageUploader.js`: Component for uploading images and displaying the generated image.
- `src/index.js`: Entry point of the React application.
- `src/App.js`: Main application component.
- `src/index.css`: Global CSS styles.
- `src/App.css`: CSS styles for the App component.

## Backend

### Installation

1. Navigate to the `backend` directory:
    ```sh
    cd backend
    ```

2. Create a virtual environment:
    ```sh
    python -m venv venv
    ```

3. Activate the virtual environment:
    - On Windows:
        ```sh
        venv\Scripts\activate
        ```
    - On macOS/Linux:
        ```sh
        source venv/bin/activate
        ```

4. Install the dependencies:
    ```sh
    pip install -r requirements.txt
    ```

### Running the Backend

1. Start the FastAPI server:
    ```sh
    uvicorn main:app --reload
    ```

2. The backend server will be running at `http://localhost:8000`.

### File Structure

- `main.py`: Main entry point of the FastAPI application.
- `src/models.py`: Contains the neural style transfer model.
- `src/utils.py`: Utility functions for image handling.
- `src/criterion.py`: Criterion for calculating the loss during training.
- `requirements.txt`: List of Python dependencies.

## Usage

1. Open the frontend application in your browser.
2. Upload a content image and a style image.
3. Click the "Upload" button to start the neural style transfer process.
4. The generated image will be displayed once the process is complete.

## Notes

- Ensure that the backend server is running before using the frontend application.
- The backend server should be accessible at `http://localhost:8000` for the frontend to communicate with it.

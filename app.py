from fastapi import FastAPI, UploadFile, Form
from pydantic import BaseModel
from typing import Dict
import requests
from PyPDF2 import PdfReader
from bs4 import BeautifulSoup
import uuid
import os
import io

app = FastAPI()
@app.get("/")
def read_root():
    return {"message": "Welcome to the FastAPI app!"}

# Storage for processed data
processed_data = {}

# BaseModel for URL request
class URLRequest(BaseModel):
    url: str

# BaseModel for Chat API
class ChatRequest(BaseModel):
    chat_id: str
    question: str

# Endpoint 1: Process Web URL API
@app.post("/process_url")
async def process_url(request: URLRequest):
    url = request.url
    try:
        # Scraping content from the URL
        response = requests.get(url)
        soup = BeautifulSoup(response.content, "html.parser")
        text = soup.get_text(separator="\n")
        
        # Generate a unique chat_id
        chat_id = str(uuid.uuid4())
        processed_data[chat_id] = text
        
        return {
            "chat_id": chat_id,
            "message": "URL content processed and stored successfully."
        }
    except Exception as e:
        return {"error": str(e)}

# Endpoint 2: Process PDF Document API
@app.post("/process_pdf")
async def process_pdf(file: UploadFile):
    try:
        # Read the uploaded PDF file
        content = await file.read()

        # Use PyPDF2 to extract text from the PDF
        pdf_text = ""
        reader = PdfReader(io.BytesIO(content))

        for page_number, page in enumerate(reader.pages):
            try:
                # Extract text from each page
                page_text = page.extract_text()
                if page_text:
                    pdf_text += page_text.strip() + " "
                else:
                    print(f"No text found on page {page_number}.")
            except Exception as e:
                print(f"Error processing page {page_number}: {e}")

        # If no text is extracted, raise an error
        if not pdf_text.strip():
            return {"error": "No readable text found in the PDF."}

        # Generate a unique chat_id and store the processed text
        chat_id = str(uuid.uuid4())
        processed_data[chat_id] = pdf_text.strip()

        return {
            "chat_id": chat_id,
            "message": "PDF content processed and stored successfully."
        }

    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}

# Endpoint 3: Chat API
@app.post("/chat")
async def chat(request: ChatRequest):
    chat_id = request.chat_id
    question = request.question
    
    if chat_id not in processed_data:
        return {"error": "Chat ID not found."}
    
    # Retrieve the processed content
    content = processed_data[chat_id]
    
    # Simple response generation logic (Can be replaced with embeddings and cosine similarity)
    if "main idea" in question.lower():
        response = content[:200]  # Extracting the first 200 characters as the "main idea"
    else:
        response = "This is a placeholder response. Implement advanced querying logic here."
    
    return {
        "response": response
    }

# To run the app: Use uvicorn
# uvicorn filename:app --reload

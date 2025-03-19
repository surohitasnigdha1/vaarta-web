from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from transformers import pipeline
from fastapi.middleware.cors import CORSMiddleware
import requests

# Initialize FastAPI app
app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

# Load pre-trained RoBERTa model for text classification
fake_news_detector = pipeline("text-classification", model="roberta-base-openai-detector")

# Define request body structure
class TextRequest(BaseModel):
    text: str

# Function to call Google Fact Check Tools API
def google_fact_check(text):
    try:
        url = "https://factchecktools.googleapis.com/v1alpha1/claims:search"
        params = {
            "query": text,
            "key": "AIzaSyCkNW1F-8MW9xq2ABxYXoHyzejHfEE5Ye0"  # Replace with your Google API key
        }
        response = requests.get(url, params=params)
        if  response.status_code == 200:
            return response.json()
        else:
            print(f"Google Fact Check API Error: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"Google Fact Check API Exception: {e}")
        return None

# Root endpoint
@app.get("/")
def read_root():
    return {"message": "Welcome to the Fake News Detector API!"}

# API endpoint to analyze text
@app.post("/analyze")
async def analyze_text(request: TextRequest):
    try:
        # Analyze the text using the RoBERTa model
        roberta_result = fake_news_detector(request.text)[0]
        print("RoBERTa Result:", roberta_result)  # Log the result

        # Call Google Fact Check Tools API
        fact_check = google_fact_check(request.text)
        print("Fact Check API Response:", fact_check)  # Log the full API response

        # Extract all sources from Google Fact Check API
        sources = []
        if fact_check and fact_check.get("claims"):
            for claim in fact_check["claims"]:
                claim_review = claim.get("claimReview", [{}])[0]
                publisher = claim_review.get("publisher", {}).get("name", "Unknown Publisher")
                url = claim_review.get("url", "#")

                # Ensure the source URL is absolute
                if url and not url.startswith(("http://", "https://")):
                    url = "#"  # Fallback if the URL is not valid

                sources.append({
                    "publisher": publisher,
                    "url": url
                })

        print("Extracted Sources:", sources)  # Log the extracted sources

        # Ensure the RoBERTa result has the expected fields
        if "label" not in roberta_result or "score" not in roberta_result:
            raise ValueError("RoBERTa model returned an unexpected result format")

        return {
            "label": roberta_result["label"],
            "confidence": roberta_result["score"],
            "sources": sources
        }
    except Exception as e:
        print("Error:", e)  # Log any errors
        raise HTTPException(status_code=500, detail=str(e))

# Run the app
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
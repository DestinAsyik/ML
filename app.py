from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
from recomContent import getRecommendationsByCategory
from recomDistance import getTempatTerdekat
import pickle

app = FastAPI()

# Load pre-trained models
with open('models/destination.pkl', 'rb') as file:
    destination = pickle.load(file)

with open('models/cosineSim.pkl', 'rb') as file:
    cosineSim = pickle.load(file)

class RecommendationRequest(BaseModel):
    category: str

class NearbyRequest(BaseModel):
    user_lat: float
    user_long: float
    top_n: Optional[int] = 10

@app.post("/recommendations/category")
def recommend_by_category(request: RecommendationRequest, limit: int = 100):
    try:
        recommendations = getRecommendationsByCategory(request.category, destination, cosineSim)
        limited_recommendations = recommendations[:limit]  
        return {"reccomContent": limited_recommendations}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during recommendation: {str(e)}")

@app.post("/recommendations/nearby")
def recommend_nearby(request: NearbyRequest):
    try:
        user_lat = float(request.user_lat)
        user_long = float(request.user_long)
        
        nearby_places = getTempatTerdekat(user_lat, user_long, destination, request.top_n)
        return {"nearby_places": nearby_places[['place_name', 'distance_km']].to_dict(orient="records")}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during nearby recommendation: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8000)
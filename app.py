from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
from recomContent import getRecommendationsByCategory
from recomDistance import getTempatTerdekat
from recomInteraction import getColaborative, model
from typing import List
import pickle
import pandas as pd

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
    
class ReviewData(BaseModel):
    user_id: int
    item_id: int
    rating: float

class CollaborativeRequest(BaseModel):
    user_id: int
    review_data: List[ReviewData]
    bookmarks: List[int] = []
    likes: List[int] = []

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
    
@app.post("/recommendations/collaborative")
def recommend_collaborative(request: CollaborativeRequest, n_recommendations: int = 15):
    try:
        user_id = request.user_id
        review_df = pd.DataFrame([review.dict() for review in request.review_data])

        # Validasi jika review_df kosong
        if review_df.empty:
            print("No review data provided. Using fallback logic.")
            recommendations = getColaborative(user_id, model, pd.DataFrame(), n_recommendations)
        else:
            review_df['is_bookmarked'] = review_df['item_id'].apply(lambda x: 1 if x in request.bookmarks else 0)
            review_df['is_liked'] = review_df['item_id'].apply(lambda x: 1 if x in request.likes else 0)
            print("Review DataFrame prepared:", review_df.head())
            recommendations = getColaborative(user_id, model, review_df, n_recommendations)

        return {"collaborative_recommendations": recommendations.tolist()}
    except Exception as e:
        print("Error during collaborative recommendation:", e)
        raise HTTPException(status_code=500, detail=f"Error during collaborative recommendation: {str(e)}")
    
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
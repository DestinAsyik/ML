import pandas as pd
import numpy as np
from tensorflow.keras.models import load_model

Destination = pd.read_csv('./data/destinasiDB.csv')
model = load_model('./models/finalModel.h5')

def getColaborative(user_id, model, data, n_recommendations=15):
    # Validasi data Destination
    if Destination.empty:
        raise ValueError("Destination database is empty. Please check your dataset.")
    if 'item_id' not in Destination.columns:
        raise ValueError("Column 'item_id' not found in Destination dataset.")

    # Ambil semua item dari basis data
    all_item_ids = Destination['item_id'].unique()  
    all_item_ids = np.array(all_item_ids)

    # Validasi data review
    if data.empty or 'item_id' not in data.columns:
        reviewed_items = np.array([])
    else:
        reviewed_items = data['item_id'].unique()

    # Kandidat item
    candidate_items = np.setdiff1d(all_item_ids, reviewed_items)

    # Fallback jika tidak ada kandidat
    if len(candidate_items) == 0:
        print("No candidate items available. Falling back to all items.")
        return all_item_ids[:n_recommendations]

    # Buat input untuk model
    user_ids = np.array([user_id] * len(candidate_items))
    bookmarked = np.zeros(len(candidate_items))  
    liked = np.zeros(len(candidate_items))  

    # Prediksi rating untuk semua kandidat
    predicted_ratings = model.predict([user_ids, candidate_items, bookmarked, liked]).flatten()

    # Pilih N item dengan skor prediksi tertinggi
    top_items = candidate_items[np.argsort(predicted_ratings)[-n_recommendations:]]
    return top_items

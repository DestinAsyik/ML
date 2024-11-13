import pandas as pd
from sklearn.preprocessing import OneHotEncoder
from sklearn.metrics.pairwise import cosine_similarity
import pickle

destination = pd.read_csv('./data/destinasiWisata.csv')

oneHotCategory = OneHotEncoder(sparse_output=False)
categoryEncoded = oneHotCategory.fit_transform(destination[['category']])
categoryEncoded = pd.DataFrame(categoryEncoded, columns=oneHotCategory.get_feature_names_out(['category']))

cosineSim = cosine_similarity(categoryEncoded)
cosineSim = pd.DataFrame(cosine_similarity(categoryEncoded), index=destination.index, columns=destination.index)

with open('models/cosineSim.pkl', 'wb') as file:
    pickle.dump(cosineSim, file)

def getRecommendationsByCategory(selected_category, destination, cosineSim, top_n=10):
    category_indices = destination[destination['category'] == selected_category].index

    if category_indices.empty:
        print("Kategori yang dipilih tidak ditemukan dalam data destinasi.")
        return []

    recommendations = []

    for idx in category_indices:
        similarity_scores = cosineSim.loc[idx]
        sorted_scores = similarity_scores.sort_values(ascending=False).iloc[1:]
        
        recommended_indices = sorted_scores.head(top_n).index
        recommended_places = destination.loc[recommended_indices, 'place_name']

        recommendations.extend(recommended_places.tolist())

    unique_recommendations = list(set(recommendations))
    
    return unique_recommendations


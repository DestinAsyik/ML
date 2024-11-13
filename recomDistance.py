import pandas as pd
from math import radians, sin, cos, sqrt, atan2
import pickle

destination = pd.read_csv('./data/destinasiWisata.csv')

destination['latitude'] = destination['latitude'].apply(lambda x: float(str(x).replace("'", "").replace("{", "").replace("}", "").split(':')[-1].strip()))
destination['longitude'] = destination['longitude'].apply(lambda x: float(str(x).replace("'", "").replace("{", "").replace("}", "").split(':')[-1].strip()))

with open('models/destination.pkl', 'wb') as file:
    pickle.dump(destination, file)

def haversine(lat1, lon1, lat2, lon2):
    R = 6371  
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    distance = R * c
    return distance

def getTempatTerdekat(user_lat, user_long, data, top_n=10):
    data['distance_km'] = data.apply(lambda row: haversine(user_lat, user_long, row['latitude'], row['longitude']), axis=1)
    nearest_places = data.sort_values(by='distance_km').head(top_n)
    return nearest_places
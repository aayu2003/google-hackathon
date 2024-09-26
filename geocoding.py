import requests
import json
import logging

# Configure logging
logging.basicConfig(level=logging.ERROR)

def gc(city,imp):                #returns the list of tuples
    # URL of the API
    url = f'https://geocode.maps.co/search?q={city}&api_key=668911db944a0630717719hiqcf6a20'

    # Send a GET request to the API
    response = requests.get(url)

    # Check if the request was successful
    if response.status_code == 200:
        # Parse the JSON response
        data = response.json()

        # Extract the coordinates
        bounding_boxes = [[place["display_name"],[place["lat"],place["lon"]]]  for place in data if place["importance"]>=imp]

        return bounding_boxes    
    else:
        logging.error(f"Failed to fetch geocoding data. Status code: {response.status_code}")
        return ()


def rev(lat:float,lon:float):
    url = f'https://geocode.maps.co/reverse?lat={lat}&lon={lon}&api_key=668911db944a0630717719hiqcf6a20'
    response = requests.get(url)
    if response.status_code == 200:
        if response.json()=={"error":"Unable to geocode"}:
            logging.error(f"the selected area is not available for delivery")

        else:
            try:
                city=response.json()["address"]["state_district"]
                city=city.split()[0].lower()
                return city
            except:
                return "city not available"
    else:
        logging.error(f"Failed to fetch geocoding data. Status code: {response.status_code}")
        return ""


import math

def haversine(lat1, lon1, lat2, lon2):
    # Convert latitude and longitude from degrees to radians
    lat1=float(lat1)
    lon1=float(lon1)
    lat2=float(lat2)
    lon2=float(lon2)
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    
    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    
    # Radius of Earth in kilometers. Use 3956 for miles.
    r = 6371
    
    # Calculate the result
    distance = c * r
    return distance

# lat1, lon1 = 28.7041, 77.1025  # Example coordinates (Delhi, India)
# lat2, lon2 = 28.4595, 77.0266  # Example coordinates (Gurugram, India)

# distance = haversine(lat1, lon1, lat2, lon2)
# print(f"Distance: {distance:.2f} km")
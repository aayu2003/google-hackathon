import requests

def find_nearest_highway(lat, lon, radius=300):
    overpass_url = "http://overpass-api.de/api/interpreter"

    # Queries for motorway, trunk, and primary highways in order
    highway_types = ['motorway', 'trunk', 'primary']
    
    # for highway_type in highway_types:
    overpass_query = f"""
    [out:json];
    way(around:{radius},{lat},{lon})[highway=primary];
    out geom;
    """
    
    # Make the request to the Overpass API
    response = requests.get(overpass_url, params={'data': overpass_query})
    
    if response.status_code == 200:
        data = response.json()
        if data['elements']:  # If the current highway type is found
            return data['elements'][0]  # Return the first found highway element

    # If none of the highway types are found, return None
    return None

# # Example coordinates (lat, lon)
# lat, lon = 21.242,81.648

# # Get the nearest highway (motorway, trunk, or primary)
# nearest_highway = find_nearest_highway(lat, lon)

# # Output the result
# print(nearest_highway)

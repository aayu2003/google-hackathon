import streamlit as st
import pydeck as pdk
import pandas as pd
import httpx  # Use httpx for async requests
from PIL import Image
import asyncio
import os
from dotenv import load_dotenv
import json
# Disable Jupyter support in pydeck
load_dotenv()   
import google.generativeai as genai
from streamlit.components.v1 import iframe
import folium
import numpy as np
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from scipy.spatial.distance import cdist
import pandas as pd
from sklearn.preprocessing import LabelEncoder
# model = genai.GenerativeModel(model_name="gemini-1.5-flash")
api_key = "AIzaSyCttE7CHlvxpD3o4bNMHi7Sj52IHPbfaTU"
genai.configure(api_key=api_key)
# os.environ['LANGCHAIN_TRACING_V2'] ="true"
# os.environ['LANGCHAIN_API_KEY'] =os.getenv("LANGCHAIN_API_KEY")
# os.environ["LANGCHAIN_ENDPOINT"]="https://api.smith.langchain.com"
# os.environ["LANGCHAIN_PROJECT"]="CREWAI"

import pydeck.bindings.deck
pydeck.bindings.deck.has_jupyter_extra = lambda: False
st.set_page_config(layout="wide")

# FastAPI URL (change this to your actual server address)
def marketing_strategy(df,dropping_columns,column_explainination):
    df = df.drop(columns=dropping_columns,axis=1)


    label_mappings = {}

    # Apply LabelEncoder to each column and store the mappings
    for column in df.columns:
        le = LabelEncoder()
        df[column] = le.fit_transform(df[column])
    
    # Store the mapping for the current column
    label_mappings[column] = dict(zip(le.classes_, le.transform(le.classes_)))
    pca = PCA(n_components=3)
    X_pca = pca.fit_transform(df)

    # Apply KMeans clustering
    kmeans = KMeans(n_clusters=10, random_state=0)
    kmeans.fit(X_pca)
    labels = kmeans.labels_
    cluster_centers = kmeans.cluster_centers_

    # Calculate the Euclidean distances from each point in X_pca to each cluster center
    distances = cdist(X_pca, cluster_centers, 'euclidean')

    # Find the index of the nearest point in X_pca to each cluster center
    nearest_indices = []
    for i in range(kmeans.n_clusters):
        # Get indices of points assigned to cluster i
        cluster_indices = np.where(labels == i)[0]
        # Select the index of the point with the minimum distance to the cluster center
        cluster_distances = distances[cluster_indices, i]
        nearest_point_index = cluster_indices[np.argmin(cluster_distances)]
        nearest_indices.append(nearest_point_index)

    l={}
    for i, idx in enumerate(nearest_indices):
        row_dict = df.loc[idx].to_dict()
        
        import json

        # Directly use the API key
        

        # Create the model
        generation_config = {
            "temperature": 1,
            "top_p": 0.95,
            "top_k": 64,
            "max_output_tokens": 8192,
            "response_mime_type": "text/plain",  # Request JSON response
        }

        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            generation_config=generation_config,
        )

        chat_session = model.start_chat(
            history=[
            ]
        )
        
        l[i]=chat_session.send_message(f'''give me a single, unique snd consised yet breif marketing strategy for a group of customer segmentation haveing the {row_dict} every index shall tell in this manner . This {row_dict} is a dictonary made my consedering many people , its not just a single person's information it is the information or an approximate information of a group  
        all the columns are in a way that {column_explainination} ''').text

    return l

API_URL = "https://hack-the-fall.onrender.com/add_city"
FORECAST_URL="https://hack-the-fall.onrender.com/demand_forecasting"

# Set up the session state for page navigation
if "page" not in st.session_state:
    st.session_state.page = "home"

def go_to_page(page):
    st.session_state.page = page

# Color mapping for each unique cluster_id
CLUSTER_COLORS = {
    0: [255, 0, 0], 1: [0, 255, 0], 2: [0, 0, 255], 3: [255, 255, 0],
    4: [255, 0, 255], 5: [0, 255, 255], 6: [128, 0, 128], 7: [128, 128, 0],
    8: [128, 0, 0], 9: [0, 128, 0], 10: [0, 0, 128], 11: [128, 128, 128]
}

# Function to send POST request asynchronously and get stores data
async def get_city_stores(city_name,list):
    timeout = httpx.Timeout(600.0)  
    async with httpx.AsyncClient(timeout=timeout) as client:
        try:
            response = await client.post(API_URL, json={"name": city_name,"suggested":list})
            response.raise_for_status()  # Ensure response is OK
            return response.json()  # Parse and return the JSON response
        except httpx.ReadTimeout:
            print(f"Request to {API_URL} timed out.")
        except httpx.HTTPStatusError as e:
            print(f"HTTP error occurred: {e}")

async def send_for_forecast(city_name, product_name,quantity=250):
    timeout = httpx.Timeout(600.0)  # Set a custom timeout of 10 seconds
    async with httpx.AsyncClient(timeout=timeout) as client:
        try:
            response = await client.post(FORECAST_URL, json={"category": product_name,"city": city_name,"quantity": quantity})
            response.raise_for_status()  # Ensure response is OK
            return response.json()  # Parse and return the JSON response
        except httpx.ReadTimeout:
            print(f"Request to {API_URL} timed out.")
        except httpx.HTTPStatusError as e:
            print(f"HTTP error occurred: {e}")

# Home page
if st.session_state.page == "home":
    st.title("CUSTOMER SEGMENTATION (MARKETING)")
    st.write("This app helps you to generate marketing strategies for different customer segments based on their characteristics.")
    st.write("Just upload a CSV file with customer data and provide descriptions for each column. The app will generate unique marketing strategies for each customer segment.")
    uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"])

# Check if a file is uploaded
    if uploaded_file is not None:
        # Read the CSV file into a pandas DataFrame
        df = pd.read_csv(uploaded_file)
        
        # Display the first few rows of the DataFrame to the user
        st.subheader("Preview of the Uploaded CSV:")
        st.write(df.head())
        
        # Single text box for the user to provide descriptions for all columns
        st.subheader("Provide a description for the columns")
        description_text = st.text_area("Enter descriptions for the columns. Format: \nColumn1: Description\nColumn2: Description\n...", height=200)
        
        # Display the description text when the user submits
        if st.button("Submit Descriptions"):
            market=marketing_strategy(df,['account_creation_date','last_login_date','last_transaction_date','user_id','name','email','location','product_affinity'],description_text)
            # st.image("/home/aryan/MY_PROJECTS/croma/WhatsApp Image 2024-11-09 at 4.53.30 PM.jpeg")
            # st.image("/home/aryan/MY_PROJECTS/croma/WhatsApp Image 2024-11-09 at 4.54.15 PM.jpeg")

            st.title("Marketing Strategies")
            print(market)
            for key, value in market.items():
                st.markdown(value)

    # Sidebar with buttons
    st.sidebar.image("Business-Aidelogo1-6-1.png", use_column_width=True)
    # st.sidebar.title("Options")
    if st.sidebar.button("Add New Offline Store"):
        go_to_page("add_store")
    # if st.sidebar.button("Previous Sales Analysis"):
    #     st.write("Functionality for previous sales analysis will be implemented here.")
    if st.sidebar.button("Demand Forecasting "):
        # st.write("Functionality for demand forecasting will be implemented here.")
        go_to_page("Demand Forecasting")
    

# Page for adding a new offline store
elif st.session_state.page == "add_store":
    st.title("Add New Offline Store")

    city = st.text_input("Enter City Name")
    product_options = ['Electronics Store', 'General Store', 'Clothes Store', 'Medical Store', 'Stationary', 'Restaurant',"Hotel","Salon/Parlor","Gym", "Footwear Store", "Furniture Store", "Hardware Store", "Book Store", "Gift Shop", "Bakery Shop", "Jewellery Shop", "Optical Store","Vehicle Showroom", "Sports Store", "Pet Store", "Grocery Store", "Liquor Store", "Cosmetics Store"]
    selected_prod=st.selectbox("Select the type of store", product_options)
    optio= ['BESIDE MAIN ROADS/HIGHWAYS', 'IN POPULAR MARKETS', 'NEARBY TOURIST PLACES', 'NEARBY AIRPORTS/RAILWAY STATIONS', 'NEARBY SCHOOLS', 'NEARBY HOSPITALS', 'NEARBY RESIDENTIAL AREAS', 'IN MALLS', 'NEARBY HOTELS/RESTAURANTS']
    if 'suggested' not in st.session_state:
        st.session_state.suggested = []
    if st.button("Get Suggestions"):
        st.session_state.suggested = []
        print(st.session_state.suggested)
        import time
        while True:
            try:
                generation_config = {
                    "temperature": 1,
                    "top_p": 0.95,
                    "top_k": 64,
                    "max_output_tokens": 8192,
                    "response_mime_type": "text/plain",  # Request JSON response
                }
                model = genai.GenerativeModel(
                model_name="gemini-1.5-flash",
                generation_config=generation_config,
                )
                
                chat_session = model.start_chat(
                    history=[
                    ]
                )
                
                response=chat_session.send_message(f''' I want to add a new {selected_prod}. I am looking for a place in {city}. I need some relevant place types from the following options:- {optio}. Strictly Return a json with 5 most relevant place types as 'keys' and reason to choose that place as 'values'. response should have items from the given options. The list should be sorted from most important place type to least important. Take factors into consideration such as :-
                                                products might need to be imported or exported should be nearer to airports and railways, attract most relevant audience from the place types according to the product, etc. No preambles or postambles. ''').text
                
                
                print(response)
                ans = json.loads(response[7:-4])  # Parse JSON, adjust slicing if necessary
                break  # Exit loop if successful

            except Exception as e:
                print(f"Error encountered: {e}. Retrying...")
                time.sleep(1) 
                    
        st.title("**Suggestions :-**")
        header = ans.keys()
        for i in header:
            st.write(f"**{i}** : {ans[i]}")
            st.session_state.suggested.append(i)
        print(st.session_state.suggested)

    # List of ptions
    #optio= [,'NEED LARGE OPEN AREAS (WAREHOUSE)','NEARBY COMPETITORS','BESIDE MAIN ROADS/HIGHWAYS', 'IN POPULAR MARKETS', 'NEARBY TOURIST PLACES', 'NEARBY RAILWAY STATIONS', 'NEARBY AIRPORTS', 'NEARBY SCHOOLS', 'NEARBY HOSPITALS', 'NEARBY RESIDENTIAL AREAS', 'IN MALLS', 'NEARBY HOTELS RESTAURANTS']

    # Multi-select widget
    
    st.title("**Modify your options :-**")
    
    
    cols = st.columns(3) 
    

    # Create a checkbox for each option
    idx=0
    for option in optio:
        with cols[idx % 3]:
            is_checked = option in st.session_state.suggested
            print(option,is_checked)
            fuck=st.checkbox(option, value=is_checked)
            if fuck:
                if not is_checked:
                    st.session_state.suggested.append(option)
            else:
                if is_checked:
                    st.session_state.suggested.remove(option)
        idx+=1
    print(st.session_state.suggested)
    
    # Display selected options
    # if st.checkbox("**NEED OPEN LAND AREA**"):
    #     quantity = st.slider(
    #     label="Select Area (sq. ft.)",
    #     min_value=100,  # Minimum quantity
    #     max_value=10000,  # Maximum quantity
    #     value=100,  # Default quantity
    #     step=100  # Step size for increase/decrease
    # )
    if st.button("Show Potential Spots"):
        if city:
            st.write(f"Fetching data for city: {city}...")

            # Get the stores data asynchronously
            city_data = asyncio.run(get_city_stores(city,st.session_state.suggested))

            # Check if valid city data is returned
            if city_data and 'stores' in city_data:
                stores = city_data['stores']
                city_lat = city_data.get('lat')
                city_long = city_data.get('long')
                city_name = city_data["name"]
                city_airports=city_data["airports"]
                city_stations=city_data["stations"]
                city_malls=city_data["malls"]
                city_hospitals=city_data["hospitals"]
                city_schools=city_data["schools"]
                city_markets=city_data["markets"]
                city_hotels=city_data["hotels"]
                cty_restaurants=city_data["restaurants"]
                st.markdown(
                    """
                    <style>
                    .title {
                        text-align: center;
                    }
                    </style>
                    """,
                    unsafe_allow_html=True
                )

                # Use st.markdown with custom class for the title
                st.markdown("<h1 class='title'>DIVIDING THE CITY RESIDENTIAL AREAS INTO SOME GROUPS</h1>", unsafe_allow_html=True)
                image = Image.open(f"plots/{city_name}_plot.png")
                st.image(image, caption="DIVIDED INTO 12 CLUSTERS", use_column_width=True)
                st.markdown("<h1 class='title'>POTENTIAL LOCATIONS FOR NEW OFFLINE STORES</h1>", unsafe_allow_html=True)
                map2={
                "BESIDE MAIN ROADS/HIGHWAYS":"rh",
                "IN POPULAR MARKETS":"market",
                "NEARBY AIRPORTS/RAILWAY STATIONS":"as",
                "NEARBY SCHOOLS":"school",
                "NEARBY HOSPITALS":"hospital",
                "NEARBY RESIDENTIAL AREAS":"ra",
                "IN MALLS":"mall",
                "NEARBY HOTELS/RESTAURANTS":"hr",
                "NEARBY TOURIST PLACES":"tp"




                }
                fd={
                    'lat': [store["coord"][0] for store in stores],
                    'lon': [store["coord"][1] for store in stores],
                    'cluster_id': [store["cluster_id"] for store in stores],
                    'houses': [store["houses"] for store in stores],
                    'score': [store["score"] for store in stores],
                    'rank': [store["rank"] for store in stores],
                    'city_name': [city_name for i in stores],
                    'id': [store["id"] for store in stores]
                }
                for i in st.session_state.suggested:
                    fd[map2[i]]=[store[map2[i]] for store in stores]


                store_locations = pd.DataFrame(fd)
                print(store_locations)
                market_locations = pd.DataFrame({
                    'lat': [store["coord"][0] for store in city_markets],
                    'lon': [store["coord"][1] for store in city_markets],
                    'icon_data': ["market" for store in city_markets],
                    'market_name': [store["name"] for store in city_markets],  # Assign the city name to each store
                    'id': [store["id"] for store in city_markets] 
                })
                print(market_locations)
                airport_locations = pd.DataFrame({
                    'lat': [store["coord"][0] for store in city_airports],
                    'lon': [store["coord"][1] for store in city_airports],
                    'icon_data': ["airport" for store in city_airports],
                    'airport_name': [store["name"] for store in city_airports],  # Assign the city name to each store
                    'id': [store["id"] for store in city_airports] 
                })
                print(airport_locations)
                station_locations = pd.DataFrame({
                    'lat': [store["coord"][0] for store in city_stations],
                    'lon': [store["coord"][1] for store in city_stations],
                    'icon_data': ["station" for store in city_stations],
                    'station_name': [store["name"] for store in city_stations],  # Assign the city name to each store
                    'id': [store["id"] for store in city_stations] 
                })
                print(station_locations)
                mall_locations = pd.DataFrame({
                    'lat': [store["coord"][0] for store in city_malls],
                    'lon': [store["coord"][1] for store in city_malls],
                    'icon_data': ["mall" for store in city_malls],
                    'mall_name': [store["name"] for store in city_malls],  # Assign the city name to each store
                    'id': [store["id"] for store in city_malls] 
                })
                print(mall_locations)
                hospital_locations = pd.DataFrame({
                    'lat': [store["coord"][0] for store in city_hospitals],
                    'lon': [store["coord"][1] for store in city_hospitals],
                    'icon_data': ["hospital" for store in city_hospitals],
                    'hospital_name': [store["name"] for store in city_hospitals],  # Assign the city name to each store
                    'id': [store["id"] for store in city_hospitals] 
                })
                print(hospital_locations)
                school_locations = pd.DataFrame({
                    'lat': [store["coord"][0] for store in city_schools],
                    'lon': [store["coord"][1] for store in city_schools],
                    'icon_data': ["school" for store in city_schools],
                    'school_name': [store["name"] for store in city_schools],  # Assign the city name to each store
                    'id': [store["id"] for store in city_schools] 
                })
                hotel_locations = pd.DataFrame({
                    'lat': [store["coord"][0] for store in city_hotels],
                    'lon': [store["coord"][1] for store in city_hotels],
                    'icon_data': ["hotel" for store in city_hotels],
                    'hotel_name': [store["name"] for store in city_hotels],  # Assign the city name to each store
                    'id': [store["id"] for store in city_hotels] 
                })
                restaurant_locations = pd.DataFrame({
                    'lat': [store["coord"][0] for store in cty_restaurants],
                    'lon': [store["coord"][1] for store in cty_restaurants],
                    'icon_data': ["restaurant" for store in cty_restaurants],
                    'restaurant_name': [store["name"] for store in cty_restaurants],  # Assign the city name to each store
                    'id': [store["id"] for store in cty_restaurants] 
                })
                

                # Map cluster colors dynamically
                store_locations['color'] = store_locations['cluster_id'].map(lambda x: CLUSTER_COLORS.get(x, [255, 255, 255]))

                # Create pydeck layer with hover tooltips
                # store_layer = pdk.Layer(
                #     "ScatterplotLayer",
                #     data=store_locations,
                #     get_position='[lon, lat]',
                #     get_radius=130,  # Adjust marker size as needed
                #     get_fill_color='[color[0], color[1], color[2]]',
                #     pickable=True
                # )
                # icon_mapping = {
                #     "hospital": {"url": "https://img.icons8.com/color/48/000000/hospital.png", "width": 128, "height": 128, "anchorY": 128},
                #     "school": {"url": "https://img.icons8.com/color/48/000000/school.png", "width": 128, "height": 128, "anchorY": 128},
                #     "mall": {"url": "https://cdn2.vectorstock.com/i/1000x1000/45/11/shopping-mall-color-icon-vector-28494511.jpg", "width": 128, "height": 128, "anchorY": 128},
                #     "airport": {"url": "https://img.icons8.com/color/48/000000/airport.png", "width": 128, "height": 128, "anchorY": 128},
                #     "station": {"url": "https://img.icons8.com/color/48/000000/train-station.png", "width": 128, "height": 128, "anchorY": 128},
                #     "market": {"url": "https://img.icons8.com/color/48/000000/shop.png", "width": 128, "height": 128, "anchorY": 128},
                #     "hotel": {"url": "https://static.vecteezy.com/system/resources/previews/038/108/233/original/hotel-icon-logo-design-template-vector.jpg", "width": 128, "height": 128, "anchorY": 128},
                #     "restaurant": {"url": "https://img.icons8.com/color/48/000000/restaurant.png", "width": 128, "height": 128, "anchorY": 128}

                # }
                # market_layer = pdk.Layer(
                #     "IconLayer",
                #     data=market_locations,
                #     get_position="[lon, lat]",  
                #     get_icon="icon_data",
                #     get_size=100,  # Adjust icon size as needed
                #     size_scale=100,  # Adjust to control the scaling of the icon
                #     pickable=True,
                #     icon_mapping=icon_mapping
                # )
                # airport_layer = pdk.Layer(
                #     "IconLayer",
                #     data=airport_locations,
                #     get_position="[lon, lat]",
                #     get_icon="icon_data",
                #     get_size=5,  # Adjust icon size as needed
                #     size_scale=10,  # Adjust to control the scaling of the icon
                #     pickable=True,
                #     icon_mapping=icon_mapping
                # )
                # station_layer = pdk.Layer(
                #     "IconLayer",
                #     data=station_locations,
                #     get_position="[lon, lat]",
                #     get_icon="icon_data",
                #     get_size=5,  # Adjust icon size as needed
                #     size_scale=10,  # Adjust to control the scaling of the icon
                #     pickable=True,
                #     icon_mapping=icon_mapping
                # )
                # mall_layer = pdk.Layer(
                #     "IconLayer",
                #     data=mall_locations,
                #     get_position="[lon, lat]",
                #     get_icon="icon_data",
                #     get_size=5,  # Adjust icon size as needed
                #     size_scale=10,  # Adjust to control the scaling of the icon
                #     pickable=True,
                #     icon_mapping=icon_mapping
                # )
                # hospital_layer = pdk.Layer(
                #     "IconLayer",
                #     data=hospital_locations,
                #     get_position="[lon, lat]",
                #     get_icon="icon_data",
                #     get_size=5,  # Adjust icon size as needed
                #     size_scale=10,  # Adjust to control the scaling of the icon
                #     pickable=True,
                #     icon_mapping=icon_mapping
                # )
                # school_layer = pdk.Layer(
                #     "IconLayer",
                #     data=school_locations,
                #     get_position="[lon, lat]",
                #     get_icon="icon_data",
                #     get_size=5,  # Adjust icon size as needed
                #     size_scale=10,  # Adjust to control the scaling of the icon
                #     pickable=True,
                #     icon_mapping=icon_mapping
                # )
                # hotel_layer = pdk.Layer(
                #     "IconLayer",
                #     data=hotel_locations,
                #     get_position="[lon, lat]",
                #     get_icon="icon_data",
                #     get_size=5,  # Adjust icon size as needed
                #     size_scale=10,  # Adjust to control the scaling of the icon
                #     pickable=True,
                #     icon_mapping=icon_mapping
                # )
                # restaurant_layer = pdk.Layer(
                #     "IconLayer",
                #     data=restaurant_locations,
                #     get_position="[lon, lat]",
                #     get_icon="icon_data",
                #     get_size=5,  # Adjust icon size as needed
                #     size_scale=10,  # Adjust to control the scaling of the icon
                #     pickable=True,
                #     icon_mapping=icon_mapping
                # )

                # Tooltip with additional store info
                # tooltip = {
                #     "html": """
                #         <b>Houses:</b> {houses}<br/>
                #         <b>Air Distance:</b> {air_dist}<br/>
                #         <b>Station Distance:</b> {station_dist}<br/>
                #         <img src="http://localhost:8000/static/{city_name}_{id}.png" alt="Store Image" width="500" height="500">
                #     """,
                #     "style": {"color": "white"}
                # }




                # Set view state to center over the city's lat/long
                # view_state = pdk.ViewState(
                #     latitude=city_lat if city_lat else 20.5937,  # Default to India's latitude
                #     longitude=city_long if city_long else 78.9629,  # Default to India's longitude
                #     zoom=10,  # Zoom level centered over the city
                #     pitch=0
                # )
                map = folium.Map(location=[city_lat,city_long], zoom_start=12)
                for _, row in hospital_locations.iterrows():
                    folium.Marker(
                        location=[row['lat'], row['lon']],
                        popup=row['hospital_name'],
                        icon=folium.CustomIcon(
                            icon_image='https://img.icons8.com/color/48/000000/hospital.png',  # Image URL
                            icon_size=(20, 20)
                        )
                    ).add_to(map)
                for _, row in school_locations.iterrows():
                    folium.Marker(
                        location=[row['lat'], row['lon']],
                        popup=row['school_name'],
                        icon=folium.CustomIcon(
                            icon_image='https://img.icons8.com/color/48/000000/school.png',  # Image URL
                            icon_size=(20, 20)
                        )
                    ).add_to(map)
                for _, row in mall_locations.iterrows():
                    folium.Marker(
                        location=[row['lat'], row['lon']],
                        popup=row['mall_name'],
                        icon=folium.CustomIcon(
                            icon_image='https://cdn2.vectorstock.com/i/1000x1000/45/11/shopping-mall-color-icon-vector-28494511.jpg',  # Image URL
                            icon_size=(20, 20)
                        )
                    ).add_to(map)
                for _, row in airport_locations.iterrows():
                    folium.Marker(
                        location=[row['lat'], row['lon']],
                        popup=row['airport_name'],
                        icon=folium.CustomIcon(
                            icon_image='https://img.icons8.com/color/48/000000/airport.png',  # Image URL
                            icon_size=(20, 20)
                        )
                    ).add_to(map)
                for _, row in station_locations.iterrows():
                    folium.Marker(
                        location=[row['lat'], row['lon']],
                        popup=row['station_name'],
                        icon=folium.CustomIcon(
                            icon_image='https://img.icons8.com/color/48/000000/train-station.png',  # Image URL
                            icon_size=(20, 20)
                        )
                    ).add_to(map)
                for _, row in market_locations.iterrows():
                    folium.Marker(
                        location=[row['lat'], row['lon']],
                        popup=row['market_name'],
                        icon=folium.CustomIcon(
                            icon_image='https://img.icons8.com/color/48/000000/shop.png',  # Image URL
                            icon_size=(20, 20)
                        )
                    ).add_to(map)
                for _, row in hotel_locations.iterrows():
                    folium.Marker(
                        location=[row['lat'], row['lon']],
                        popup=row['hotel_name'],
                        icon=folium.CustomIcon(
                            icon_image='https://static.vecteezy.com/system/resources/previews/038/108/233/original/hotel-icon-logo-design-template-vector.jpg',  # Image URL
                            icon_size=(20, 20)
                        )
                    ).add_to(map)
                for _, row in restaurant_locations.iterrows():
                    folium.Marker(
                        location=[row['lat'], row['lon']],
                        popup=row['restaurant_name'],
                        icon=folium.CustomIcon(
                            icon_image='https://img.icons8.com/color/48/000000/restaurant.png',  # Image URL
                            icon_size=(20, 20)
                        )
                    ).add_to(map)
                for _, row in store_locations.iterrows():
                    folium.CircleMarker(
                        location=[row['lat'], row['lon']],
                        radius=8,  # Marker size
                        color=f'rgba({row["color"][0]}, {row["color"][1]}, {row["color"][2]}, 1)',  # Color based on cluster
                        fill=True,
                        fill_color=f'rgba({row["color"][0]}, {row["color"][1]}, {row["color"][2]}, 0.6)',  # Semi-transparent fill
                        fill_opacity=1,
                        popup=f"Rank: {row['rank']}\nScore:{row['score']}\nCluster ID:{row['cluster_id']}",  # Tooltip with Cluster ID or other info
                    ).add_to(map)
                map.save("pages/map.html")

                # Display the Folium map in Streamlit
                st.write(f"### Map of {city_name}")
                import streamlit.components.v1 as components

# Displaying map.html directly
                with open("pages/map.html", "r") as f:
                    html_content = f.read()
                    components.html(html_content, height=1000, width=1700)
                # Sort stores by score in descending order
                store_locations = store_locations.sort_values(by='score', ascending=False)

# Display store details with color-coded containers
                st.header("Overall Ranking of Potential Spots")
                index=1
                for _, row in store_locations.iterrows():
                    color = row['color']
                    bg_color = f'rgba({color[0]}, {color[1]}, {color[2]}, 0.2)'  # Light background color for container
                    border_color = f'rgba({color[0]}, {color[1]}, {color[2]}, 1)'  # Border color to match cluster color

                    # Display store info with a color-coded container
                    container_html = f"""
                    <div style="
                        background-color: {bg_color}; 
                        border-left: 5px solid {border_color}; 
                        padding: 10px; 
                        border-radius: 5px; 
                        margin-bottom: 10px;
                    ">
                        <b>Rank:</b> {index}<br>
                        <b>Cluster ID:</b> {row['cluster_id']}<br>
                        <b>Score:</b> {row['score']}<br>
                        <b>Houses:</b> {row['houses']}<br>
                    """
                    
                    # Add dynamic fields based on st.session_state.suggested
                    for field in st.session_state.suggested:
                        if map2[field] in row and row[map2[field]]!=-1:
                            # field_label = field.replace('_', ' ').title()
                            container_html += f"<b>{field}:</b> {row[map2[field]]:.2f} Km.<br>"
                    index+=1
                    # Close the HTML container
                    container_html += "</div>"
                    st.markdown(container_html, unsafe_allow_html=True)
                # st.pydeck_chart(pdk.Deck(
                #     layers=[store_layer,market_layer,airport_layer,station_layer,mall_layer,hospital_layer,school_layer,hotel_layer,restaurant_layer],
                #     initial_view_state=view_state,
                #     tooltip=tooltip
                # ))
            else:
                st.warning(f"No store data found for city: {city}")
        else:
            st.warning("Please enter a city name.")

    if st.button("Go Back"):
        go_to_page("home")

# Page for demand forecasting
elif st.session_state.page == "Demand Forecasting":
    st.title("Demand Forecasting (Trending Products)")
   

    


    # Create input form to capture product name and city name
    with st.form(key='forecast_form'):
        product_name = st.text_input("Enter the Product Name")
        city_name = st.text_input("Enter the City Name")
        
        # Submit button
        submit_button = st.form_submit_button(label='Submit')

        

    # When the form is submitted
    if submit_button:
        # Replace with your actual backend API endpoint
        
        st.write(f"Forecasting demand for {product_name} in {city_name}... (THIS MIGHT TAKE UPTO 2 MINS)")
        result=asyncio.run(send_for_forecast(city_name, product_name))

        forecast_data = result
        print(forecast_data["products"])
        # Convert the JSON data to a DataFrame for better display
        df = pd.DataFrame(forecast_data["products"])
        

        # Display the forecast summary
        st.write(f"**City:** {forecast_data['city']}")
        st.write(f"**City Type:** {forecast_data['city_type']}")
        st.write(f"**Demand Summary:** {forecast_data['demand_summary']}")

        # Display the forecasted products in tabular form
        st.write("### Forecasted Products")
        st.table(df[['model_name', 'specifications', 'target_customer','trending_level', 'no_of_units_forcasted', 'price']])
            
        


    # Go back to home button
    if st.button("Go Back"):
        go_to_page("home")





#f4c5812fc8
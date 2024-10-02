import streamlit as st
import pydeck as pdk
import pandas as pd
import httpx  # Use httpx for async requests
from PIL import Image
import asyncio

# Disable Jupyter support in pydeck

import pydeck.bindings.deck
pydeck.bindings.deck.has_jupyter_extra = lambda: False
st.set_page_config(layout="wide")

# FastAPI URL (change this to your actual server address)

API_URL = "http://localhost:8000/add_city"
FORECAST_URL="http://localhost:8000/demand_forecasting"

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
async def get_city_stores(city_name):
    timeout = httpx.Timeout(600.0)  # Set a custom timeout of 10 seconds
    async with httpx.AsyncClient(timeout=timeout) as client:
        try:
            response = await client.post(API_URL, json={"name": city_name})
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
    st.title("Croma Sales Analysis   (show sales analysis and competitor analysis here)")
    image = st.image("Electronics.jpg", caption="Electronics Store", use_column_width=True)

    # Sidebar with buttons
    st.sidebar.title("Options")
    if st.sidebar.button("Add New Offline Store"):
        go_to_page("add_store")
    # if st.sidebar.button("Previous Sales Analysis"):
    #     st.write("Functionality for previous sales analysis will be implemented here.")
    if st.sidebar.button("Demand Forecasting"):
        # st.write("Functionality for demand forecasting will be implemented here.")
        go_to_page("Demand Forecasting")
    

# Page for adding a new offline store
elif st.session_state.page == "add_store":
    st.title("Add New Offline Store")

    city = st.text_input("Enter City Name")

    if st.button("Show Potential Spots"):
        if city:
            st.write(f"Fetching data for city: {city}... (THIS MIGHT TAKE UPTO 5 MINS)")

            # Get the stores data asynchronously
            city_data = asyncio.run(get_city_stores(city))

            # Check if valid city data is returned
            if city_data and 'stores' in city_data:
                stores = city_data['stores']
                city_lat = city_data.get('lat')
                city_long = city_data.get('long')
                city_name = city_data["name"]
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
                st.markdown("<h1 class='title'>DISTANCE BASED CLUSTERING OF HOUSES AND BUILDINGS</h1>", unsafe_allow_html=True)
                image = Image.open(f"plots/{city_name}_plot.png")
                st.image(image, caption="DIVIDED INTO 12 CLUSTERS", use_column_width=True)
                st.markdown("<h1 class='title'>POTENTIAL SPOTS FOR NEW CROMA STORES</h1>", unsafe_allow_html=True)
                store_locations = pd.DataFrame({
                    'lat': [store["coord"][0] for store in stores],
                    'lon': [store["coord"][1] for store in stores],
                    'cluster_id': [store["cluster_id"] for store in stores],
                    'houses': [store["houses"] for store in stores],
                    'air_dist': [store["air_dist"] for store in stores],
                    'station_dist': [store["station_dist"] for store in stores],
                    'city_name': [city_name for i in stores],  # Assign the city name to each store
                    'id': [store["id"] for store in stores] 
                })

                # Map cluster colors dynamically
                store_locations['color'] = store_locations['cluster_id'].map(lambda x: CLUSTER_COLORS.get(x, [255, 255, 255]))

                # Create pydeck layer with hover tooltips
                map_layer = pdk.Layer(
                    "ScatterplotLayer",
                    data=store_locations,
                    get_position='[lon, lat]',
                    get_radius=130,  # Adjust marker size as needed
                    get_fill_color='[color[0], color[1], color[2]]',
                    pickable=True
                )

                # Tooltip with additional store info
                tooltip = {
                    "html": """
                        <b>Houses:</b> {houses}<br/>
                        <b>Air Distance:</b> {air_dist}<br/>
                        <b>Station Distance:</b> {station_dist}<br/>
                        <img src="http://localhost:8000/static/{city_name}_{id}.png" alt="Store Image" width="500" height="500">
                    """,
                    "style": {"color": "white"}
                }




                # Set view state to center over the city's lat/long
                view_state = pdk.ViewState(
                    latitude=city_lat if city_lat else 20.5937,  # Default to India's latitude
                    longitude=city_long if city_long else 78.9629,  # Default to India's longitude
                    zoom=10,  # Zoom level centered over the city
                    pitch=0
                )

                # Display the map with stores
                st.pydeck_chart(pdk.Deck(
                    layers=[map_layer],
                    initial_view_state=view_state,
                    tooltip=tooltip
                ))
            else:
                st.warning(f"No store data found for city: {city}")
        else:
            st.warning("Please enter a city name.")

    if st.button("Go Back"):
        go_to_page("home")

# Page for demand forecasting
elif st.session_state.page == "Demand Forecasting":
    st.title("Demand Forecasting")
   

    


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
        st.table(df[['model_name', 'specifications', 'trending_level', 'no_of_units_forcasted', 'price']])
            
        


    # Go back to home button
    if st.button("Go Back"):
        go_to_page("home")
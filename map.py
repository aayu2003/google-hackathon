#takes city name , makes a raw map according to the geocode.
import folium


def make_map(L,city):
        # L -> location coordinate list
        #creates the map according to geocode and returns the location where map is saved
        my_map1 = folium.Map(location=L, zoom_start=12)

        # Add the satellite tile layer
        tile = folium.TileLayer(
        tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
        attr='Esri',
        name='Esri Satellite',
        overlay=False,
        control=True
        ).add_to(my_map1)

        # Add a WMS layer for land cover data (example: Copernicus Global Land Cover)
        folium.raster_layers.WmsTileLayer(
        url='https://services.terrascope.be/wms/v2',
        name='Land Cover',
        layers='WORLDCOVER_2020_MAP',
        attr='Copernicus Global Land Service',
        fmt='image/png',
        transparent=True,
        overlay=True,
        control=True
        ).add_to(my_map1)

        # Save the map to an HTML file
        my_map1.save(f"seg_map/{city}.html")
        
        return f"seg_map/{city}.html"


def make_map_satellite(L,city):
        my_map1 = folium.Map(location=L, zoom_start=12)
        tile = folium.TileLayer(
        tiles = 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
        attr = 'Esri',
        name = 'Esri Satellite',
        overlay = False,
        control = True
        ).add_to(my_map1)

        my_map1.save(f"seg_map/satellite/{city}.html")
        
        return f"seg_map/satellite/{city}.html"



def land_zoom(L,city,id):
        my_map1 = folium.Map(location=L, zoom_start=18)
        tile = folium.TileLayer(
        tiles = 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
        attr = 'Esri',
        name = 'Esri Satellite',
        overlay = False,
        control = True
        ).add_to(my_map1)
        folium.Marker(
        location=L,
        popup="Store",
        icon=folium.Icon(icon="store", prefix='fa')
        ).add_to(my_map1)
        my_map1.save(f"land_zoom/H/{city}_{id}.html")
        
        return f"land_zoom/H/{city}_{id}.html"


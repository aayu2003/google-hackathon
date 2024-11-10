from fastapi import FastAPI,Depends,status,Response, HTTPException,File,UploadFile, Form, Request, BackgroundTasks
from database import engine, get_db
import tables
from sqlalchemy.orm import Session
from typing import List
from fastapi.middleware.cors import CORSMiddleware
# from fastapi.responses import HTMLResponse
# from jinja2 import Template
# from schemas import UserLogin,UserSignup, Token, CreateOrder,AP,PO,appro
from api import get_chat_session
# from google import generativeai as genai
from crew import TripCrew
# from datetime import timedelta
# import logging
from schemas import City, demand
from geocoding import gc
from map import make_map,make_map_satellite
from geocoding import gc,rev,haversine
from selen import save_ss,save_ss_satellite,selen_zoom
from cluster import make_cluster,make_cluster_land
from highway import find_nearest_highway
import math
from tools import search_internet,scrape
import json
import os
from dotenv import load_dotenv
import inspect
app=FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust according to your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
load_dotenv()


from fastapi.staticfiles import StaticFiles

# Mount the 'land_zoom/img' directory
# app.mount("/static", StaticFiles(directory="land_zoom/img"), name="static")

tables.Base.metadata.create_all(engine) 

def convert_to_coord(k,top,left):
    return [top-k[0]*(0.312/1080),left+k[1]*(0.644/1920)]
def pic_dist(a,b,c,d):
    return math.sqrt((a-c)**2+(b-d)**2)

# def process_new_stores(stores, city):
#     # The snippet to run in the background
#     for st in stores:
#         H_path = land_zoom(st["coord"], city, st["id"])
#         selen_zoom(city, H_path, st["id"])


def get_variable_name(var):
    frame = inspect.currentframe().f_back
    return [k for k, v in frame.f_locals.items() if v is var]
@app.post('/add_city',status_code=status.HTTP_200_OK, tags=["Admin"])
async def add_city(city:City, db: Session = Depends(get_db)):
    sugg=city.suggested
    city = city.name # Read the body of the request
    
    # city = city.decode('utf-8')  # Decode the bytes to string
    city = str(city)  # Convert the string to lowercase
    cityy= city.lower()
    print(cityy)
    c =  gc(cityy,0)  # if geocode doesn't exist it returns an empty list.
    if len(c):
        check_db = db.query(tables.City).filter((tables.City.lat==c[0][1][0]) & (tables.City.long==c[0][1][1])).first()
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"{city} not found")
    
    # Markets = gc(cityy + " market",0)
    if not check_db:
            Airports = gc(cityy + " airport",0.4)                                                  # first scrape airport name, then search geocode
            Stations= gc(cityy + " railway",0.4)
            Malls=gc(cityy + " mall",0)
            Hospitals=gc(cityy + " hospital",0)
            Markets=gc(cityy + " market",0)
            Hotels=gc(cityy + " hotel",0)
            Restaurants=gc(cityy + " restaurant",0)
            Schools=gc(cityy + " school",0)
            path = make_map(c[0][1], cityy)
            satellite_path=make_map_satellite(c[0][1],cityy)
            img_path = save_ss(cityy, path)
            sat_img=save_ss_satellite(cityy,satellite_path)
            r = make_cluster_land(img_path,sat_img)           
            r2,NP=make_cluster(img_path,sat_img,cityy)                    
            # dont ADD those stations which are very far from house clusters
            final_stations=[]
            print(3847)
            for j in r:
                print("it 0")
                GCC=convert_to_coord(j,float(c[0][1][0])+0.156,float(c[0][1][1])-0.322)
                FAR=haversine(GCC[0],GCC[1],float(c[0][1][0]),float(c[0][1][1]))
                # FAR=haversine(GCC[0],GCC[1],float(c[0][1][0]),float(c[0][1][1]))
                if FAR>12:
                    continue
                road = find_nearest_highway(GCC[0], GCC[1])
                
                print("it 1")
                if road:
                
                    CL = min([(idx,pic_dist(j[0],j[1],i[0],i[1])) for idx,i in enumerate(r2)], key=lambda x: x[1])[0]
                    final_stations.append((j,CL,NP[CL]))
            print(1)
            airports=[{"id":i,"name": Airport[0], "coord": Airport[1]} for i,Airport in enumerate(Airports) ]
            stations=[{"id":i,"name": Airport[0], "coord": Airport[1]} for i,Airport in enumerate(Stations) ]
            malls=[{"id":i,"name": Mall[0], "coord": Mall[1]} for i,Mall in enumerate(Malls) ]
            hospitals=[{"id":i,"name": Hospital[0], "coord": Hospital[1]} for i,Hospital in enumerate(Hospitals) ]
            markets=[{"id":i,"name": Market[0], "coord": Market[1]} for i,Market in enumerate(Markets) ]
            hotels=[{"id":i,"name": Hotel[0], "coord": Hotel[1]} for i,Hotel in enumerate(Hotels) ]
            restaurants=[{"id":i,"name": Restaurant[0], "coord": Restaurant[1]} for i,Restaurant in enumerate(Restaurants) ]
            schools=[{"id":i,"name": School[0], "coord": School[1]} for i,School in enumerate(Schools) ]
            print("airports : ", airports)
            print("stations : ", stations)
            print("malls : ", malls)
            print("hospitals : ", hospitals)
            print("markets : ", markets)
            print("hotels : ", hotels)
            print("restaurants : ", restaurants)
            print("schools : ", schools)
            map={
                "BESIDE MAIN ROADS/HIGHWAYS":[],
                "IN POPULAR MARKETS":markets,
                "NEARBY AIRPORTS/RAILWAY STATIONS":airports+stations,
                "NEARBY SCHOOLS":schools,
                "NEARBY HOSPITALS":hospitals,
                "NEARBY RESIDENTIAL AREAS":[],
                "IN MALLS":malls,
                "NEARBY HOTELS/RESTAURANTS":hotels+restaurants,
                "NEARBY TOURIST PLACES":[]




            }
            potential_list=[]
            only_lists=[]
            for i in sugg:
                potential_list.extend(map[i])
                only_lists.append((i,map[i]))
            def how_many_stores(n):
                if n<=5000:
                    return 1
                elif n>5000 and n<15000:
                    return 3
                elif n>=15000 and n<25000:
                    return 5
                elif n>=25000:
                    return 7

            
            clusters=[{"id": idx, "coord": convert_to_coord(coord,float(c[0][1][0])+0.156,float(c[0][1][1])-0.322),"houses":i} for idx, (i, coord) in enumerate(zip(NP,r2))]
            # stores=[{"id": i, "coord": convert_to_coord(coord[0],float(c[0][1][0])+0.156,float(c[0][1][1])-0.322),"cluster_id":coord[1],"houses":coord[2],"air_dist":"","station_dist":""} for i, coord in enumerate(final_stations) ]
            # print(2)
            # print(len(stores))
            old_city = tables.City(                                    
                name=cityy,                                     
                lat=float(c[0][1][0]),                                
                long=float(c[0][1][1]),
                clusters=[{"id": int(idx), "coord": convert_to_coord(coord,float(c[0][1][0])+0.156,float(c[0][1][1])-0.322),"houses":int(i)} for idx, (i, coord) in enumerate(zip(NP,r2))],
                stores=[{"id": int(i), "coord": convert_to_coord(coord[0],float(c[0][1][0])+0.156,float(c[0][1][1])-0.322),"cluster_id":int(coord[1]),"houses":int(coord[2])} for i, coord in enumerate(final_stations) ],
                airports=[{"id":i,"name": Airport[0], "coord": Airport[1]} for i,Airport in enumerate(Airports) ],
                stations=[{"id":i,"name": Airport[0], "coord": Airport[1]} for i,Airport in enumerate(Stations) ],
                malls=[{"id":i,"name": Mall[0], "coord": Mall[1]} for i,Mall in enumerate(Malls) ],
                hospitals=[{"id":i,"name": Hospital[0], "coord": Hospital[1]} for i,Hospital in enumerate(Hospitals) ],
                markets=[{"id":i,"name": Market[0], "coord": Market[1]} for i,Market in enumerate(Markets) ],
                hotels=[{"id":i,"name": Hotel[0], "coord": Hotel[1]} for i,Hotel in enumerate(Hotels) ],
                restaurants=[{"id":i,"name": Restaurant[0], "coord": Restaurant[1]} for i,Restaurant in enumerate(Restaurants) ],
                schools=[{"id":i,"name": School[0], "coord": School[1]} for i,School in enumerate(Schools) ]
                
       # ADD airport distancs, station distance and highway distance in stores directly, also add score of each store, highest=true for the highest of each cluster
            )
            
            # for st in new_stores:
            #     H_path=land_zoom(st["coord"],cityy,st["id"])
            #     selen_zoom(cityy,H_path,st["id"])
            db.add(old_city)
            db.commit()
            db.refresh(old_city)
            print("added old city")
            return "added city details"
            
            # db.add(new_city)
            # db.commit() 
            # db.refresh(new_city)
            # Return the city data
            # print("done")
            # background_tasks.add_task(process_new_stores, new_stores, cityy)
            
            
            
       
    else:
        # Return the city data
        Airports=check_db.airports
        Stations=check_db.stations
        Malls=check_db.malls
        Hospitals=check_db.hospitals
        Markets=check_db.markets
        Hotels=check_db.hotels
        Restaurants=check_db.restaurants
        Schools=check_db.schools
        clusters=check_db.clusters
        map={
                "BESIDE MAIN ROADS/HIGHWAYS":[],
                "IN POPULAR MARKETS":Markets,
                "NEARBY AIRPORTS/RAILWAY STATIONS":Airports+Stations,
                "NEARBY SCHOOLS":Schools,
                "NEARBY HOSPITALS":Hospitals,
                "NEARBY RESIDENTIAL AREAS":[],
                "IN MALLS":Malls,
                "NEARBY HOTELS/RESTAURANTS":Hotels+Restaurants,
                "NEARBY TOURIST PLACES":[]




            }
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
        potential_list=[]
        only_lists=[]
        for i in sugg:
            potential_list.extend(map[i])
            only_lists.append((i,map[i]))
        def how_many_stores(n):
            if n<=5000:
                return 1
            elif n>5000 and n<15000:
                return 3
            elif n>=15000 and n<25000:
                return 5
            elif n>=25000:
                return 7
        stores=check_db.stores
        clusters=check_db.clusters
        print("alreadt exists")
        new_stores=[]
        for cl in clusters:
            c_stores=[]
            cou=how_many_stores(cl["houses"])
            print(cou)
            # finding nearest railway station or airport whatever is near
            for st in range(len(stores)):
                if stores[st]["cluster_id"]==cl["id"]:
                    coeff=-10
                    score=0
                        # mindist=min(haversine(stores[st]["coord"][0],stores[st]["coord"][1],float(i["coord"][0]),float(i["coord"][1])) for i in potential_list)
                    for sublist in only_lists:
                        mindist=-1
                        if len(sublist[1]):
                            mindist=min(haversine(stores[st]["coord"][0],stores[st]["coord"][1],float(i["coord"][0]),float(i["coord"][1])) for i in sublist[1])
                            
                            score+=coeff*mindist
                        stores[st][sublist[0]]=mindist
                        coeff+=2
                    stores[st]["score"]=score
                    print(score)
                        # if len(airports):
                        #     stores[st]["air_dist"]=min(haversine(stores[st]["coord"][0],stores[st]["coord"][1],float(i["coord"][0]),float(i["coord"][1])) for i in airports)
                        # if len(stations):
                        #     stores[st]["station_dist"]=min(haversine(stores[st]["coord"][0],stores[st]["coord"][1],float(i["coord"][0]),float(i["coord"][1])) for i in stations)
                        
                    
                    
                    # if len(potential_list):
                    # elif len(airports):
                    #     mindist=min(haversine(stores[st]["coord"][0],stores[st]["coord"][1],float(i["coord"][0]),float(i["coord"][1])) for i in airports)
                    #     stores[st]["air_dist"]=min(haversine(stores[st]["coord"][0],stores[st]["coord"][1],float(i["coord"][0]),float(i["coord"][1])) for i in airports)
                    # elif len(stations):
                    #     mindist=min(haversine(stores[st]["coord"][0],stores[st]["coord"][1],float(i["coord"][0]),float(i["coord"][1])) for i in stations)
                    #     stores[st]["station_dist"]=min(haversine(stores[st]["coord"][0],stores[st]["coord"][1],float(i["coord"][0]),float(i["coord"][1])) for i in stations)
                    c_stores.append([stores[st],score])

            c_stores.sort(key=lambda x: x[1],reverse=True)
            for i in range(len(c_stores)):
                c_stores[i][0]["rank"]=i+1
            if c_stores and len(c_stores)>=cou:
                new_stores.extend([ij[0] for ij in c_stores[:cou]])
            else:
                if not c_stores:
                    continue
                new_stores.extend([ij[0] for ij in c_stores])   
        
        final=[]
        for i in new_stores:
            di={"id":int(i["id"]),"coord":i["coord"],"cluster_id":int(i["cluster_id"]),"houses":int(i["houses"]), "score":i["score"],"rank":i["rank"]}
            for j in only_lists:
                di[map2[j[0]]]=i[j[0]]
            final.append(di)
            
        new_city = tables.City(                                    
            name=cityy,                                     
            lat=float(c[0][1][0]),                                
            long=float(c[0][1][1]),
            clusters=clusters,
            stores=final,
            airports=Airports,
            stations=Stations,
            malls=Malls,
            hospitals=Hospitals,
            markets=Markets,
            hotels=Hotels,
            restaurants=Restaurants,
            schools=Schools
            

            # ADD airport distancs, station distance and highway distance in stores directly, also add score of each store, highest=true for the highest of each cluster

        )
        return new_city
        
    


@app.get("/chat",status_code=status.HTTP_200_OK,  tags=["Chat"])
async def chat(user_id: str, message: str):
    # Get or create the chat session for this user
    chat_session = get_chat_session(user_id)

    # Send the user's message to the model and get the response
    response = chat_session.send_message(message)

    # Return the bot's response
    return {"response": response.text}

from collections import defaultdict
Price_seg = defaultdict(lambda: "Assume according to scrapped data")

Price_seg["smartphones"]={
    "high":" above 60000 rupees",
    "mid":" between 20000 and 60000 rupees",
    "low":" below 20000 rupees"
}
Price_seg["laptops"]={
    "high":" above 80000 rupees",
    "mid":" between 30000 and 80000 rupees",
    "low":" between 20000 and 30000 rupees",
    "NOTE": "Don't keep any laptop below 20000 rupees"
}
Price_seg["headphones"]={
    "high":" above 15000 rupees",
    "mid":" between 3000 and 15000 rupees",
    "low":" below 3000 rupees"
}
Price_seg["washing machines"]={
    "high":" above 40000 rupees",
    "mid":" between 15000 and 40000 rupees",
    "low":" below 15000 rupees"
}
Price_seg["refrigerators"]={
    "high":" above 60000 rupees",
    "mid":" between 20000 and 60000 rupees",
    "low":" below 20000 rupees"
}


@app.post("/demand_forecasting",status_code=status.HTTP_200_OK, tags=["Demand Forecasting"])
async def demand_forecasting(info:demand):
    category = str(info.category)
    city = str(info.city)
    q=str(info.quantity)


    print("## WELCOME TO DEMAND FORECASTING CREW")
    print('-------------------------------')
  
    jsons=search_internet(f"Trending {category} 2024 india")
    
    print("\nSCRAPPING THE LINKS\n")
    FULL=[]
    CITY="""
    Decoding Indian Cities
Classifications In Tier I, II, III
In the vast expanse of India, cities emerge as vibrant hubs of commerce,
culture, and opportunity. To comprehend and navigate this diverse urban
landscape, the Indian government has classified cities into four distinct tiers:
Tier I, II, III. These classifications serve as valuable indicators,
shedding light on factors such as population size, infrastructure development,
economic growth, and quality of life. This article aims to delve into the
intricacies of these city classifications, unravelling the characteristics and
implications associated with each tier.
Join us on this insightful journey as we decode the classifications shaping
India's urban fabric

Purpose Of Tier Classification For Cities

Cities are classified into tiers for the following reasons:
1. Administrative efficiency: Tier classification allows governments to
manage and govern cities more effectively by providing a framework for
resource allocation, policy implementation, and decision-making.
2. Economic assessment: Tiers help assess a city's economic strength
and potential, enabling businesses and investors to identify lucrative
markets and opportunities for growth.
3. Urban planning and infrastructure: Classification assists in urban
planning initiatives and infrastructure development by prioritising
resource allocation and ensuring appropriate attention to cities in need of
development.
4. Investment considerations: Tiers help businesses and investors
evaluate potential markets based on the size of the consumer base,
business environment, and purchasing power of cities. 
5. Quality of life assessment: The tier system serves as an indicator of a
city's overall quality of life and social development, guiding policymakers
and researchers in identifying areas for improvement and resource
allocation.


Definition And Parameters Of City Classification Tiers

The classification of Indian cities into different tiers is a methodical
categorisation based on specific parameters. These parameters encompass
population size, economic development, infrastructure, educational institutions,
healthcare facilities, and administrative importance. By considering these
factors, the tier system provides a structured framework for understanding the
varying degrees of urbanisation, development, and opportunities across cities
in India.
1. Population Size: The size of a city's population plays a pivotal role in
determining its tier classification. Tier I cities have the largest population,
followed by Tier II, III cities. 
2. Economic Development: The economic indicators, such as gross
domestic product (GDP), employment opportunities, and per capita
income, are crucial parameters for city-tier assessment. Higher-tier cities
generally exhibit greater economic activity and a more robust business
environment.
3. Infrastructure: The level of infrastructure development is a significant
criterion for city classification. Tier I cities are characterised by welldeveloped transportation networks, modern airports, extensive
roadways, and advanced communication systems. Infrastructure
gradually becomes less developed as we move down the tiers. 
Educational Institutions and Healthcare Facilities: The presence of
educational institutions and healthcare facilities is considered when
classifying cities. Tier I cities often have prestigious universities,
research institutions, and top-notch healthcare centres. The availability
and quality of these facilities may vary as we move to lower-tier cities.
5. Administrative Importance: The administrative importance of a city,
particularly its role as a state or regional administrative centre, also
influences its tier classification. Cities with significant administrative
functions tend to be placed in higher tiers.


Tier I Cities: Thriving Urban Centres

Tier I cities in India represent the epitome of urban development, offering a
wealth of opportunities and amenities. Here are some notable Tier I cities in
India, including Bengaluru, Delhi, Chennai, Hyderabad, Mumbai,
Pune, Kolkata, and Ahmedabad.
These cities serve as major economic, commercial, and cultural hubs, drawing
both national and international attention. They boast exceptional infrastructure,
world-class educational institutions, and diverse industries. These Tier I cities
attract a diverse population, fostering cultural diversity and innovation, and
offer abundant employment opportunities.

Tier 2 cities : Emerging Urban Centres
bhopal , bhubneshwar, nagpur, patna, raipur, ranchi, surat, vadodara, visakhapatnam, indore, etc.

Tier 3 cities : Developing Urban Centres
gwalior, jabalpur, jodhpur, kochi, kozhikode, ludhiana, madurai, meerut, nashik, rajkot, etc.





    """
    for i in jsons:
        content = scrape(i['link'])
        FULL.append(content)
        
    print("\nSCRAPPING DONE\n")
    
    # for i in city_info:
    #     content = scrape(i)
    #     CITY.append(content)

    

  
    trip_crew = TripCrew(category, q,"\n\n".join(FULL),city,CITY,Price_seg[category])
    # trip_crew = TripCrew(category, quantity,"no data")
    result = trip_crew.run()
    print("\n\n########################")
    print("## Here is you Forecasting result")
    print("########################\n")
    print(result)
    # output_dict = result.model_dump()
    # Convert string to dictionary
    print(result[-7:-4])
    my_dict = json.loads(result[7:-4])

    # output_json = json.dumps(output_dict)
    # print(output_dict)
    # print(type(output_dict))
    # f=1
    # for i in output_dict.keys():
    #     if f>=len(output_dict)-1:
    #         break
    #     print(i)
    #     print("\n\n\n")
    #     print(output_dict[i])
    #     f+=1
    
    # print(my_dict[:10])
    # print(type(my_dict))
    print(type(my_dict))
    return my_dict
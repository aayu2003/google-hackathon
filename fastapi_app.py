from fastapi import FastAPI,Depends,status,Response, HTTPException,File,UploadFile, Form, Request
from database import engine, get_db
import tables
from sqlalchemy.orm import Session
from typing import List
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from jinja2 import Template
# from schemas import UserLogin,UserSignup, Token, CreateOrder,AP,PO,appro
from datetime import timedelta
import logging
from schemas import City
from geocoding import gc
from map import make_map,make_map_satellite,land_zoom
from geocoding import gc,rev,haversine
from selen import save_ss,save_ss_satellite,selen_zoom
from cluster import make_cluster,make_cluster_land
from highway import find_nearest_highway
import math
app=FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust according to your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from fastapi.staticfiles import StaticFiles

# Mount the 'land_zoom/img' directory
app.mount("/static", StaticFiles(directory="land_zoom/img"), name="static")

tables.Base.metadata.create_all(engine) 

def convert_to_coord(k,top,left):
    return [top-k[0]*(0.312/1080),left+k[1]*(0.644/1920)]
def pic_dist(a,b,c,d):
    return math.sqrt((a-c)**2+(b-d)**2)

@app.post('/add_city',status_code=status.HTTP_200_OK, tags=["Admin"])
async def add_city(city:City, db: Session = Depends(get_db)):
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
            Stations= gc(cityy + " railway",0.45)
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
                if FAR>10:
                    continue
                road = find_nearest_highway(GCC[0], GCC[1])
                
                print("it 1")
                if road:
                
                    CL = min([(idx,pic_dist(j[0],j[1],i[0],i[1])) for idx,i in enumerate(r2)], key=lambda x: x[1])[0]
                    final_stations.append((j,CL,NP[CL]))
            print(1)
            airports=[{"id":i,"name": Airport[0], "coord": Airport[1]} for i,Airport in enumerate(Airports) ]
            stations=[{"id":i,"name": Airport[0], "coord": Airport[1]} for i,Airport in enumerate(Stations) ]

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
            stores=[{"id": i, "coord": convert_to_coord(coord[0],float(c[0][1][0])+0.156,float(c[0][1][1])-0.322),"cluster_id":coord[1],"houses":coord[2],"air_dist":"","station_dist":""} for i, coord in enumerate(final_stations) ]
            print(2)
            print(len(stores))
            new_stores=[]
            for cl in clusters:
                c_stores=[]
                cou=how_many_stores(cl["houses"])
                print(cou)
                for st in range(len(stores)):
                    if stores[st]["cluster_id"]==cl["id"]:
                        mindist=0
                        if len(airports) and len(stations):
                            mindist=min(haversine(stores[st]["coord"][0],stores[st]["coord"][1],float(i["coord"][0]),float(i["coord"][1])) for i in airports+stations)
                            stores[st]["air_dist"]=min(haversine(stores[st]["coord"][0],stores[st]["coord"][1],float(i["coord"][0]),float(i["coord"][1])) for i in airports)
                            stores[st]["station_dist"]=min(haversine(stores[st]["coord"][0],stores[st]["coord"][1],float(i["coord"][0]),float(i["coord"][1])) for i in stations)
                        elif len(airports):
                            mindist=min(haversine(stores[st]["coord"][0],stores[st]["coord"][1],float(i["coord"][0]),float(i["coord"][1])) for i in airports)
                            stores[st]["air_dist"]=min(haversine(stores[st]["coord"][0],stores[st]["coord"][1],float(i["coord"][0]),float(i["coord"][1])) for i in airports)
                        elif len(stations):
                            mindist=min(haversine(stores[st]["coord"][0],stores[st]["coord"][1],float(i["coord"][0]),float(i["coord"][1])) for i in stations)
                            stores[st]["station_dist"]=min(haversine(stores[st]["coord"][0],stores[st]["coord"][1],float(i["coord"][0]),float(i["coord"][1])) for i in stations)
                        c_stores.append([stores[st],mindist])

                c_stores.sort(key=lambda x: x[1])
                if c_stores and len(c_stores)>=cou:
                    new_stores.extend([ij[0] for ij in c_stores[:cou]])
                else:
                    if not c_stores:
                        continue
                    new_stores.extend([ij[0] for ij in c_stores])
            for st in new_stores:
                H_path=land_zoom(st["coord"],cityy,st["id"])
                selen_zoom(cityy,H_path,st["id"])
            new_city = tables.City(                                    
                name=cityy,                                     
                lat=float(c[0][1][0]),                                
                long=float(c[0][1][1]),
                clusters=[{"id": int(idx), "coord": convert_to_coord(coord,float(c[0][1][0])+0.156,float(c[0][1][1])-0.322),"houses":int(i)} for idx, (i, coord) in enumerate(zip(NP,r2))],
                stores=[{"id":int(i["id"]),"coord":i["coord"],"cluster_id":int(i["cluster_id"]),"houses":int(i["houses"]),"air_dist":i["air_dist"],"station_dist":i["station_dist"]} for i in new_stores],
                airports=[{"id":i,"name": Airport[0], "coord": Airport[1]} for i,Airport in enumerate(Airports) ],
                stations=[{"id":i,"name": Airport[0], "coord": Airport[1]} for i,Airport in enumerate(Stations) ]
                

                # ADD airport distancs, station distance and highway distance in stores directly, also add score of each store, highest=true for the highest of each cluster

            )
            db.add(new_city)
            db.commit()
            db.refresh(new_city)
            # Return the city data
            print("done")
            return new_city
            
            
       
    else:
        # Return the city data
        print("alreadt exists")
        return check_db
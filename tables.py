from sqlalchemy import Column, Integer, String, JSON,Float, ForeignKey,Boolean
from database import Base
from sqlalchemy.orm import relationship   #use this to make relationships between user and products, see that part again


class City(Base):
    __tablename__='cities'
    id=Column(Integer,primary_key=True,index=True)
    name=Column(String)
    lat=Column(Float)
    long=Column(Float)
    stores = Column(JSON)  # JSON column for station details   
    airports=Column(JSON)
    stations=Column(JSON)
    clusters=Column(JSON)  # k means cluster centers
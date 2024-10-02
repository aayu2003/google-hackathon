# pass quandtity = nd*nds + fd*fds


from crewai import Crew,Process
from textwrap import dedent
from tasks import TripTasks
from agents import TripAgents
from dotenv import load_dotenv
from tools import search_internet,scrape
load_dotenv()

class TripCrew:

  def __init__(self, category, quantity,data,city,incity,price_seg):
    self.category =category
    self.quantity = quantity
    self.data=data
    self.city=city
    self.incity=incity
    self.price_seg=price_seg

  def run(self):
    
    tasks = TripTasks()
    agents = TripAgents()
    forecaster_agent = agents.make_forecaster()
    researcher_agent = agents.make_researcher()
    # scrapper_agent=agents.scrapper()
    exploration_task = tasks.Explore(
      researcher_agent,
      self.category,
      self.data,
      self.price_seg
    )
    forecasting_task = tasks.Forecast(
      forecaster_agent,
      self.category,
      self.quantity,
      self.city,
      self.incity
    )
    output_task = tasks.aggregate(
      researcher_agent, 
      self.category
    )
    # scrappp_task=tasks.scrappp(scrapper_agent)

    crew = Crew(
      agents=[
        researcher_agent,forecaster_agent
      ],
      tasks=[exploration_task, forecasting_task, output_task],
      verbose=True,
      process=Process.sequential
    )

    result = crew.kickoff()
    return result

city_info=[
    "https://www.99acres.com/articles/list-of-cities-in-india.html",
    "https://www.360realtors.com/blog/post/understanding-indian-city-classification-in-tier-i-ii-iii-and-iv-blid749#:~:text=In%20India%2C%20there%20are%2097%20tier%202%20cities%2C,Jaipur%2C%20Kochi%2C%20Patna%2C%20Lucknow%2C%20Agra%2C%20Kanpur%2C%20and%20Srinagar."
]

if __name__ == "__main__":

  print("## WELCOME TO DEMAND FORECASTING CREW")
  print('-------------------------------')
  category = input(
    dedent("""
      which electronics store are you working for? :
    """))
  quantity = input(
    dedent("""
      enter quantity :
    """))
  city=input(
    dedent("""
      enter the city:
    """))
  jsons=search_internet(f"Trending {category} 2024 india")
  
  print("SCRAPPING THE LINKS")
  FULL=[]
  for i in jsons:
    content = scrape(i['link'])
    FULL.append(content)
  CITY="""
Decoding Indian Cities
Classifications In Tier I, II, III, IV
In the vast expanse of India, cities emerge as vibrant hubs of commerce,
culture, and opportunity. To comprehend and navigate this diverse urban
landscape, the Indian government has classified cities into four distinct tiers:
Tier I, II, III, and IV. These classifications serve as valuable indicators,
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
followed by Tier II, III, and IV cities. 
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

Tier II Cities: Emerging Urban Centres

Tier II cities in India are witnessing rapid growth and urbanisation, presenting
promising opportunities for development. Here are some notable Tier II cities in
India, including Amritsar, Bhopal, Bhubaneswar, Chandigarh, Faridabad,
Ghaziabad, Jamshedpur, Jaipur, Kochi, Lucknow, Nagpur, Patna, Raipur,
Surat, Visakhapatnam, Agra, Ajmer, Kanpur, Mysuru, and Srinagar.
These Tier II cities are experiencing significant economic and infrastructural
advancements, attracting investments and fostering business growth. They
offer a range of industries, educational institutions, and healthcare facilities,
catering to the needs of their growing populations. 

Tier III Cities: Growing Urban Centres

Tier III cities in India are emerging as significant centres of growth and
development. Here are some notable Tier III cities, including Amritsar, Bhopal,
Bhubaneswar, Chandigarh, Faridabad, Ghaziabad, Jamshedpur, Jaipur,
Kochi, Lucknow, Nagpur, Patna, Raipur, Surat, Visakhapatnam, Agra, Ajmer,
Kanpur, Mysuru, and Srinagar.
These cities are witnessing rapid urbanisation and are experiencing
advancements in infrastructure, industry, and services. They offer a range of
opportunities in sectors such as manufacturing, IT services, healthcare,
education, and more. Tier III cities are becoming attractive destinations for
investment and are playing a crucial role in the economic growth of their
respective regions

Tier IV Cities: Developing Urban Centres

Tier IV cities in India encompass smaller urban centres and towns that are
gradually experiencing growth and development. Among these Tier IV cities
are Banswara, Bhadreswar, Chilakaluripet, Datia, Gangtok, Kalyani,
Kapurthala, Kasganj, Nagda, and Sujangarh.
These cities may have more limited amenities compared to higher-tier
counterparts, but they offer unique opportunities and contribute to the regional
economy. Each city showcases its own distinct local culture, industries, and
natural resources. As these Tier IV cities continue to evolve, efforts are being
made to enhance infrastructure, promote investment, and improve the quality
of life for their residents.
Banswara, Bhadreswar, Chilakaluripet, Datia, Gangtok, Kalyani, Kapurthala,
Kasganj, Nagda, and Sujangarh are all playing a vital role in fostering inclusive
growth and providing employment opportunities within their respective regions.
These cities represent the diversity and potential found in the evolving
landscape of Tier IV urban centres in India.

Government Initiatives: Driving Urban Development

The Indian government has launched key initiatives to drive urban
development:
1. Smart Cities Mission: Transforming 100 cities, including Tier II and III,
into sustainable and citizen-friendly urban centres through improved
infrastructure and smart solutions.
2. Atal Mission for Rejuvenation and Urban Transformation (AMRUT):
Providing basic infrastructure and services in Tier II, III, and IV cities,
focusing on water supply, sanitation, urban transport, and green spaces.
3. Pradhan Mantri Awas Yojana (PMAY): Urban: Ensuring affordable
housing for all by 2022, with financial assistance and subsidies for
construction and renovation projects.
4. Swachh Bharat Mission (Urban): Achieving cleanliness and sanitation
in urban areas, eliminating open defecation, and promoting waste
management and hygiene practices.
5. Urban Infrastructure Development Scheme for Small and Medium
Towns (UIDSSMT): Strengthening urban infrastructure in Tier III and IV
cities, improving water supply, roads, drainage systems, and essential
urban facilities. 

These initiatives demonstrate the government's commitment to inclusive urban
development, promoting sustainable growth and improving the quality of life for
residents across different tiers of cities.

Implications And Future Prospects

The classification of Indian cities into tiers has significant implications for
regional development, economic opportunities, infrastructure, and employment
patterns. By understanding these implications and considering future
prospects, policymakers can foster balanced growth and create a sustainable
urban landscape.
1. Balanced Development: The tier classification system helps direct
resources and investments towards different cities, promoting balanced
regional development and reducing disparities.
2. Economic Opportunities: Tier I cities attract investments and offer
abundant employment opportunities, but leveraging the potential of
lower-tier cities can decentralise economic activities and unlock growth
in smaller urban centres
3. Infrastructure Development: The tier classification guides
infrastructure planning, necessitating the enhancement of connectivity
and amenities in lower-tier cities to improve quality of life and attract
investments.
4. Employment and Migration: Tier I cities experience significant
migration, straining infrastructure. Developing lower-tier cities can create
employment opportunities closer to hometowns, reducing migration and
easing pressure on major urban centres.
5. Future Prospects: The classification system should be periodically
reviewed and updated to reflect evolving urban landscapes. Future
prospects lie in leveraging each tier's strengths, promoting sustainability,
and creating inclusive cities. 


Real Estate Trends In Tier-I, II, III, IV Cities: An OvervieW
The real estate sector in India experiences varying trends and dynamics
across different tiers of cities. Here is an overview of the real estate trends in
each tier, highlighting the key factors driving the market: 

Tier-I Cities:
Bengaluru, Delhi, Chennai, Hyderabad, Mumbai, Pune, Kolkata, and
Ahmedabad are Tier-I cities with mature real estate markets.
High demand for residential and commercial properties due to robust
economic activities and employment opportunities.
Rising property prices, especially in prime locations, are driven by limited land
availability and high population density.
Increasing focus on integrated townships, luxury apartments, and smart homes
to cater to the lifestyle preferences of the urban population.
Growth in co-working spaces and flexible office spaces to accommodate the
changing work culture.
Tier-II Cities:
Amritsar, Bhopal, Bhubaneswar, Chandigarh, Faridabad, Ghaziabad,
Jamshedpur, Jaipur, Kochi, Lucknow, Nagpur, Patna, Raipur, Surat,
Visakhapatnam, Agra, Ajmer, Kanpur, Mysuru, and Srinagar fall under Tier-II
cities with emerging real estate markets. 
Increasing investment opportunities, improved infrastructure, and expanding
economic activities are driving the real estate sector.
Growing demand for affordable housing, mid-segment residential projects, and
commercial spaces.
Rise in organised retail and shopping malls to cater to the changing consumer
preferences.
Development of industrial parks and special economic zones (SEZs) attracting
commercial and industrial investments.

Tier-III Cities:
Tier-III cities like Banswara, Bhadreswar, Chilakaluripet, Datia, Gangtok,
Kalyani, Kapurthala, Kasganj, Nagda, and Sujangarh are witnessing gradual
real estate development.
Increasing interest from investors and developers due to lower land costs and
untapped potential.
Focus on affordable housing projects, especially for first-time homebuyers and
middle-income groups.
Growing demand for commercial spaces, particularly in sectors like education,
healthcare, and hospitality.
Infrastructure development initiatives and improved connectivity are boosting
real estate activities in these cities.
Tier-IV Cities:
Tier-IV cities consist of smaller urban centres and towns across the country,
with emerging real estate markets.
Limited real estate activities primarily focused on local needs and regional
development.
Growing demand for residential properties, including plotted developments and
smaller housing projects.
Development of local markets, small shopping complexes, and retail outlets to
cater to the local population.
Focus on sustainable and eco-friendly construction practices in line with the
growing awareness of environmental impact.
Conclusion
In conclusion, the real estate trends in Tier-I, II, III, and IV cities reflect the
diverse dynamics of India's urban landscape. Tier-I cities continue to
experience high demand and rising property prices, while Tier-II cities witness
emerging opportunities for investment and development. Tier-III and IV cities,
on the other hand, show gradual growth and increasing focus on affordable
housing. Understanding these trends helps stakeholders navigate the real
estate market and capitalise on the opportunities presented by each tier.
"""
    
  print("SCRAPPING DONE")
  
  import json
  trip_crew = TripCrew(category, quantity,"\n\n".join(FULL),city,CITY)
  # trip_crew = TripCrew(category, quantity,"no data")
  result = trip_crew.run()
  print("\n\n########################")
  print("## Here is you Forecasting result")
  print("########################\n")
  print(result)
  output_dict = result.model_dump()
  # output_json = json.dumps(output_dict)
  print(output_dict)
  print(type(output_dict))
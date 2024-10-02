from crewai import Agent
from litellm import completion
from dotenv import load_dotenv
from tools import search_internet, calculate , scrape
load_dotenv()

import os

os.environ['GEMINI_API_KEY'] =os.getenv("GOOGLE_API_KEY")
llm=completion(
    model="gemini/gemini-1.5-flash",
    messages=[{"role": "user", "content": "write code for saying hi from LiteLLM"}]
)

"""
role : just the name of the agent
goal : what the agent is supposed to do and return exactly
backstory : agentt's resume
"""
class TripAgents:
    def make_researcher(self):
        return Agent(
            role="Trending products researcher",
            goal="""Search the trending electronic products of the selected category and extract useful information. ignore the garbage, focus only on what is required. STRICTLY SELECT 40 MODELS ONLY OF GIVEN ELECTRONIC !!.  "Don't include any unpopular or irrelevant products which costs too high or too low!" . Keep most of the products in the medium price range . some products in high price range and few products in low price range. Categorise the final answer based on the price and sort according to descending order.""",
            verbose=True,
            memory=True,
            backstory=(
                "Expert in analysing new and latest web pages related to trending electronic products of given category, and extracting product information. EXTRACT MAX 40 MODELS ONLY. This information will be used by an electronics store to understand the market trends and customer preferences for demand forecasting and inventory management. You are also expert in arranging products in descending order based on the price."
            ),
            llm="gemini/gemini-1.5-flash"
        )
    
    # def scrapper(self):
    #     return Agent(
    #         role="Webpage scrapper",
    #         goal="""Scrape all the links/URL of web pages returned by the 'trending product researcher' agent and return the cleaned text of the webpage to the researcher agent. If any website is unscrappable, leave it and srape other websites.""",
    #         verbose=True,
    #         memory=True,
    #         backstory=(
    #             "Expert in scraping the content of the webpage and returning the cleaned text. This cleaned text will be used by the researcher agent to extract the product information."
    #         ),
    #         llm="gemini/gemini-1.5-flash",
    #         tools=[scrape],
    #         allow_delegation=True
    #     )
    def make_forecaster(self):
        return Agent(
            role="Inventory forecaster for the elctronics store",
            goal="""Find the city type and demands, Forecast the demand (number of units) for each selected model for the upcoming days, according to the past year sales data and the city type.
            . Make sure the sum of all forecasted units is strictly equal to the quantity sold during this period last year""",
            verbose=True,
            memory=True,
            backstory=(
                "Expert selecting most relevant products acording to city demands . Expert in forecasting the demand of selected products for the upcoming days in an electronics store. The forecasted demand will help the store in managing inventory and planning marketing strategies. "
            ),
            llm="gemini/gemini-1.5-flash"
        )
    

  
# try with/ without scraper, allow delegation
# working with .toml ? better than conda?  



# Include category only for tasks. (because agents are general and tasks are specific)
# create tools always for agents only
# delegation = False, when you know one agent can do particular task fully (try and comment more)
#verbose means more loggings
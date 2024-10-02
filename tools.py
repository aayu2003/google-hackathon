# getenv? vs getenviron   

# always use pydantic for custom tools??






from scrap import scrapp
from crewai_tools import SerperDevTool
from dotenv import load_dotenv
from langchain.tools import tool as ltl
from pydantic import BaseModel, Field
load_dotenv()
import os   
import json, requests
# we can create custom tools too - use pydantic to make custom search and calculation tool

# search_tool=SerperDevTool(
#     api_key=os.getenv("SERPER_API_KEY"),
#     verbose=True
# )



class calculationInput(BaseModel):
    operation: str = Field(...,  description="The mathematical operation to be calculated (string containing just numbers and operators)")


class customScrape(BaseModel):
    url: str = Field(..., description="The URL/link of the webpage to scrape")



# class SearchTools():

# @ltl("Search the internet")
def search_internet(query):
    """Useful to search the internet about a a given topic and return relevant results"""
    url = "https://google.serper.dev/search"
    top_result_to_return = 20
    payload = json.dumps({
    "q": query
    })
    headers = {
    'X-API-KEY': os.getenv("SERPER_API_KEY"),
    'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    print(response.text)
    # check if there is an organic key
    if 'organic' not in response.json():
      return "Sorry, I couldn't find anything about that, there could be an error with you serper api key."
    else:
      results = response.json()['organic']
      string = []
      for result in results[:top_result_to_return]:
        try:
          string.append({
                "title": result['title'],
                "link": result['link'],
                "snippet": result['snippet']
          })
        except KeyError:
          next

      return string

    

# @ltl("Scrape A Webpage",args_schema=customScrape,return_direct=True)
def scrape(url:str):
   """Scrape the given webpage and return the text content"""

   ans=scrapp(url)
   print(ans)
   return ans
   






@ltl("Make a calculation",args_schema=calculationInput,return_direct=True)
def calculate(operation:str) -> str:
    """Calculate the given mathematical operation and return the result. the expression should be a string containing just numbers and operators
    use it to find the number of products for each price segment"""
    
    try :
        ans = eval(operation)
        return "The result of operation is : "+str(ans)
    except SyntaxError:
        return "ERROR: INVALID SYNTAX IN MATHEMATICAL EXPRESSION"
    



from crewai import Task
from textwrap import dedent


class TripTasks:

    def Forecast(self, agent, category,quantity,city,CITY):
        return Task(
            description=dedent(f"""Uncover the Buyer Trends in {city} for {category}! 
Your mission: Determine if the city :{city} is a tier 1, tier 2, or tier 3 city. Let's explore the types of {category} buyers and capture a quick summary of demand in this region! Use below data only.
Scraped data from internet: {CITY}

Based on last year's data, a total of {quantity} {category} were sold during this period. STRICTLY MAKE SUM OF ALL FORECASTED UNITS TO BE AROUND {quantity}!.

Demand Forecasting Strategy: 
Tier 1 City (Metro Cities/ IT hubs/ Large population): keep some of the TOTAL UNITS ({quantity}) high priced, most medium priced and keep few low-priced products.
Tier 2 City (Capitals/Large Urban Districts): keep few high priced, most medium priced products, and few low-priced models.
Tier 3 City (Towns/Districts): keep very few of the TOTAL UNITS high priced, most medium priced, few low priced models.


                

                {self.__tip_section()}
            """),
            agent=agent,
            expected_output=f"tell the type of city (tier 1,2 or 3).small summary of demand in that region, Then output a list of {category} and their forcasted units. example : 'xyz : 15 units'. 'STRICTLY MAKE SUM OF ALL FORECASTED UNITS TO BE AROUND {quantity}!'"
        )
    



    def Explore(self, agent, category,data,prange):
        return Task(
            # here also include city preferences (like people want high priced ones or settel for low priced ones)
            description=dedent(f"""
                Get Ready to Discover the Hottest Products in Trending {category}! 

Dive into the world of {category} as you uncover a dazzling array of products that are making waves in the market!  You'll select standout products that not only shine in performance but also currently popular in the market.
There should be diversity in specifications in the selected models. MAKE SURE TO : "Don't include any unpopular or irrelevant models which costs too high or too low!" . "STRICTLY SELECT TOTAL 40 MOST TRENDING MODELS. NOT MORE OR LESS THAN THAT PLEASE !"

Here's what you need to extract for each product:

Model Name: What's the name of this model?
Specifications:(GIVE IN ONE LINE BUT DETAILED!)
Target Customer: Who's the ideal user for this product? 
Trending Level: (high , medium, low)
You'll be on the lookout for those remarkable {category} that stand out from the crowd! From budget-friendly options to premium picks, you'll want it all. 

Select most of the products which comes under medium price range ,some products in high price range , and very few products in low price range.
price range for {category} : 
{prange}.

Select products from below data :-
SCRAPPED DATA FROM INTERNET:
{data}
                 
                {self.__tip_section()}      
            """),
            agent=agent,
            expected_output=f"Comprehensive details of trending {category} including model name, specifications, target customers, trending level, price (INR) . STRICTLY SELECT TOTAL 40 MOST TRENDING MODELS. NOT MORE OR LESS THAN THAT PLEASE ! Keep most of the products in the medium price range . some products in high range and few in low range. "
        )
    def aggregate(self,agent,category):                            
        return Task(
            description=dedent(f"""
                Create a returnable list of JSON objects by aggregation all information in detail.
                final answer must be a detailed list of trending {category} with each JSON object having the elements :- 
                model name, specifications (detailed), target customer (according to their use cases) (keep it detailed),
                trending level (high/medium/low) , number of units forcasted, price (INR). The final result should be on the basis of forecasted units.

                {self.__tip_section()}
            """),
            agent=agent,
            expected_output="final answer should contain 'city','city type' (tier 1,2 or 3), 'demand_summary' (small summary of demand in that region and reason of product forecast),'products' (list of JSON object ,each having elemets:- 'model_name', 'specifications', 'target_customer' (according to their use cases), trending_level (high/medium/low) , 'no_of_units_forcasted',  'price'). output only JSON. Sort the products according to price in descending order.",
            # output_json=OutputModel

        )

    def __tip_section(self):
        return "If you do your BEST WORK, I'll tip you $100!"
    



    

    
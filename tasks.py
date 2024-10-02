from crewai import Task
from textwrap import dedent

market_research_websites={
    "smartphones":["91mobiles","https://www.91mobiles.com/hub/91mobiles-great-indian-smartphone-survey-2024-summary/"],
    "laptops":["https://www.6wresearch.com/market-takeaways-view/laptop-market-size-with-10-prominent-companies-in-india-2024","idc.com"],
    "smartwatches":[],
    "headphones":[],
    "speakers":[],
    "cameras":[],
    "televisions":[],
    "refrigerators":[],
    "washing machines":[],
    "air conditioners":["bluewaveconsulting"],
    "microwave ovens":[],
    "vacuum cleaners":[],
    "water purifiers":[],
    "Tablets":[],
    "printers":[],
    "projectors":[],
    "room heaters":[],
    "fans":[],
    "gysers":[],
    "chimneys":[],
}
class TripTasks:

    def Forecast(self, agent, category,quantity,city,CITY):
        return Task(
            description=dedent(f"""Uncover the Buyer Trends in {city} for {category}! 
Your mission: Determine if the vibrant city :{city} is a tier 1, tier 2, or tier 3 city. Let's explore the types of {category} buyers and capture a quick summary of demand in this region! Use below data only. Don't use tool for this sub task.
Scraped data from internet: {CITY}

Based on last year's data, a total of {quantity} {category} were sold during this period. STRICTLY MAKE SUM OF ALL FORECASTED UNITS TO BE AROUND {quantity}!.

Demand Forecasting Strategy: 
Tier 1 City (Metro Cities/ IT hubs/ Large population): keep some of the TOTAL UNITS ({quantity}) high priced, most medium priced and keep few low-priced products.
Tier 2 City (Capitals/Large Urban Districts): few high priced, most medium priced products, and few low-priced models.
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
There should be diversity in specifications. MAKE SURE TO : "Don't include any unpopular or irrelevant products which costs too high or too low!" . "STRICTLY KEEP THE NUMBER OF MODELS TO 40. NOT MORE OR LESS THAN THAT PLEASE !"

Here's what you need to extract for each product:

Model Name: What's the name of this model?
Specifications:(GIVE IN ONE LINE BUT DETAILED!)
Target Customer: Who's the ideal user for this product? 
Trending Level: (high , medium, low)
You'll be on the lookout for those remarkable {category} that stand out from the crowd! From budget-friendly options to premium picks, you'll want it all. 

Keep most of the products in the medium price range . some products in high range and few in low range.
price range for {category} : {prange}.

Select products from below data :-
SCRAPPED DATA FROM INTERNET:
{data}
                 
                {self.__tip_section()}
            """),
            agent=agent,
            expected_output=f"Comprehensive details of trending {category} including model name, specifications, target customers, trending level, price (INR) . STRICTLY SELECT 40 MODELS ONLY. NOT MORE OR LESS THAN THAT PLEASE ! Keep most of the products in the medium price range . some products in high range and few in low range. "
        )
    def aggregate(self,agent,category):                            
        return Task(
            description=dedent(f"""
                Create a returnable list of JSON objects by aggregation all information in detail.
                final answer must be a detailed list of trending {category} with each JSON object having the elements :- 
                model name, specifications (detailed), target customer (according to their use cases) (keep it detailed),
                trending level (high/medium/low) , number of units forcasted, price (INR). The final result should be on the basis of forecasted units.

                " DON'T USE 'MAKE A CALCULATION' TOOL FOR THIS TASK "
                {self.__tip_section()}
            """),
            agent=agent,
            expected_output="final answer should contain 'city','city type' (tier 1,2 or 3), 'demand_summary' (small summary of demand in that region and reason of product forecast),'products' (list of JSON object ,each having elemets:- 'model_name', 'specifications', 'target_customer' (according to their use cases), trending_level (high/medium/low) , 'no_of_units_forcasted',  'price'). output only JSON. Sort the products according to price in descending order.",
            # output_json=OutputModel

        )

    def __tip_section(self):
        return "If you do your BEST WORK, I'll tip you $100!"
    



    

    
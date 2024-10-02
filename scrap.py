# import requests
# from bs4 import BeautifulSoup

# # URL of the webpage to scrape
# url = 'https://www.croma.com/unboxed/best-3-star-acs'

# # Send a GET request to the webpage
# response = requests.get(url)

# # Check if the request was successful
# if response.status_code == 200:
#     # Parse the HTML content
#     soup = BeautifulSoup(response.content, 'html.parser')
#     clean_text = BeautifulSoup(str(soup), 'html.parser').get_text(strip=True)
#     # Define the tags you want to scrape content from
#     # tags = ['a', 'p', 'li', 'span', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6']
#     print(clean_text)
#     # tags=["p","span","h1","h2","h3"]
#     # # Extract and print content from the specified tags
#     # for tag in tags:
#     #     elements = soup.find_all(tag)
#     #     for element in elements:
#     #         # Clean the text and print it
#     #         text = element.get_text(strip=True)
#     #         if text:  # Only print non-empty text
#     #             print(f"<{tag}>: {text}")

# else:
#     print(f"Failed to retrieve webpage. Status code: {response.status_code}")


import requests
from bs4 import BeautifulSoup
import re

# URL of the webpage to scrape

def scrapp(url):
    try:

# Send a GET request to the webpage
        response = requests.get(url)

        # Check if the request was successful
        
            
        if response.status_code == 200:
            # Parse the HTML content
            response = requests.get(url)

            # Parse the HTML content with BeautifulSoup
            soup = BeautifulSoup(response.content, 'html.parser')

            # Extract all text content from the page
            text_content = soup.get_text()

            # Optionally clean up the text (e.g., remove excess whitespace)
            cleaned_text = ' '.join(text_content.split())

            return cleaned_text
                    # return "\n".join(maal)

        else:
            return f"Failed to retrieve webpage. Status code: {response.status_code}"
    except:
        return f"Failed to retrieve webpage"
# print(scrapp("https://www.statista.com/statistics/1018500/india-leading-ac-providers-market-share/"))




# # Fetch the page content
# url = 'https://example.com'  # Replace with the URL you want to scrape


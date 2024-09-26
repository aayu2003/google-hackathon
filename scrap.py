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
url = 'https://www.croma.com/unboxed/best-3-star-acs'

# Send a GET request to the webpage
response = requests.get(url)

# Check if the request was successful
if response.status_code == 200:
    # Parse the HTML content
    soup = BeautifulSoup(response.content, 'html.parser')

    # Convert the parsed HTML into a string
    html_content = str(soup)

    # Define the regex pattern for the tags of interest (a, p, li, span, h1-h6)
    pattern = re.compile(r'<(a|p|li|span|h[1-6])[^>]*>(.*?)</\1>', re.S)

    # Find all content that matches the regex
    matches = pattern.findall(html_content)

    # Print content in the order it appears in the HTML
    for tag, content in matches:
        clean_text = BeautifulSoup(content, 'html.parser').get_text(strip=True)  # Clean the inner content
        if clean_text:
            print(f"<{tag}>: {clean_text}")

else:
    print(f"Failed to retrieve webpage. Status code: {response.status_code}")

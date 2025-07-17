from playwright.sync_api import sync_playwright, Playwright
from bs4 import BeautifulSoup
import requests
import time
import os
import json

search = input('What do you want to search for? ')
search_clean = search.strip().lower().replace(" ", "_")
scroll_num_of_times = int(input('How many pages do you wish to scroll through? '))

path = os.path.join("../henna_images", search_clean)
os.makedirs(path, exist_ok=True)

def run(playwright: Playwright) -> None: 
    #launch browser
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()

    page.goto(f"https://www.pinterest.com/search/pins/?q={search}")
    page.get_by_placeholder("Search").fill(search)
    page.keyboard.press("Enter")

    time.sleep(5)

    for _ in range(1, scroll_num_of_times):
        page.mouse.wheel(0,4000)
        time.sleep(2)

    html = page.inner_html('div.vbI.XiG')

    soup = BeautifulSoup(html, 'lxml')

    metadata = []

    for links in soup.find_all('img'):
        image_url = links.get('src')
        if not image_url:
            continue
        name = image_url.split("/")[-1]

        with open(os.path.join(path, name), "wb") as f:
            image = requests.get(image_url)
            f.write(image.content)
            time.sleep(2)

        metadata.append({
            "filename": name,
            "description": search,
            "full_path": os.path.join(search_clean, name)
        })
    
    with open(os.path.join(path, "metadata.json"), "w") as f:
        json.dump(metadata, f, indent=2)
    
    context.close()
    browser.close()

with sync_playwright() as playwright: 
    run(playwright)

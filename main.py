import json
import requests
import time
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator
from datetime import datetime
from urllib.parse import urljoin

def scrape_site(config):
    print(f"--- Processing {config['name']} ---")
    
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    try:
        response = requests.get(config['url'], headers=headers, timeout=15)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        fg = FeedGenerator()
        fg.title(config['name'])
        fg.link(href=config['url'], rel='alternate')
        fg.description(f"Latest news from {config['name']}")

        items = soup.select(config['container'])
        
        for item in items[:15]:
            # 1. Title & Link
            title_node = item.select_one(config['title_css'])
            if not title_node: continue
            
            title = title_node.get_text(strip=True)
            link = urljoin(config['url'], title_node['href'])

            # 2. Description
            desc_node = item.select_one(config['desc_css'])
            description = desc_node.get_text(strip=True) if desc_node else ""

            # 3. Image
            img_node = item.select_one(config['img_css'])
            img_url = urljoin(config['url'], img_node['src']) if img_node else None

            # 4. Time (Parsing SNRT's "DD/MM/YYYY - HH:MM" format)
            time_node = item.select_one(config['time_css'])
            pub_date = datetime.now() # Fallback
            if time_node:
                try:
                    raw_time = time_node.get_text(strip=True)
                    # Adjust format string to match site: %d/%m/%Y - %H:%M
                    pub_date = datetime.strptime(raw_time, '%d/%m/%Y - %H:%M')
                    # Set a timezone (UTC) to make the feed valid
                    pub_date = pub_date.astimezone() 
                except: pass

            # Create Feed Entry
            fe = fg.add_entry()
            fe.title(title)
            fe.link(href=link)
            fe.description(description)
            fe.pubDate(pub_date)
            
            if img_url:
                fe.enclosure(img_url, 0, 'image/jpeg')

        fg.rss_file(config['filename'])
        print(f"Success: {config['filename']} generated.")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    with open('sites.json', 'r') as f:
        for site in json.load(f):
            scrape_site(site)

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
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        fg = FeedGenerator()
        fg.title(config['name'])
        fg.link(href=config['url'], rel='alternate')
        fg.description(f"Latest updates from {config['name']}")

        items = soup.select(config['container'])
        
        for item in items[:15]:
            title_node = item.select_one(config['title_css'])
            if not title_node: continue
            
            title = title_node.get_text(strip=True)
            link = urljoin(config['url'], title_node['href'])
            description = item.select_one(config['desc_css']).get_text(strip=True) if item.select_one(config['desc_css']) else ""
            
            # Image extraction
            img_node = item.select_one(config['img_css'])
            img_url = urljoin(config['url'], img_node['src']) if img_node and img_node.has_attr('src') else None

            # Time parsing for SNRT format: 02/02/2026 - 09:10
            time_node = item.select_one(config['time_css'])
            pub_date = datetime.now().astimezone()
            if time_node:
                try:
                    raw_time = time_node.get_text(strip=True)
                    pub_date = datetime.strptime(raw_time, '%d/%m/%Y - %H:%M').astimezone()
                except: pass

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
        print(f"Error scraping {config['name']}: {e}")

if __name__ == "__main__":
    try:
        with open('sites.json', 'r') as f:
            sites_list = json.load(f)
        for site in sites_list:
            scrape_site(site)
    except json.JSONDecodeError as e:
        print(f"CRITICAL ERROR: sites.json is formatted incorrectly: {e}")
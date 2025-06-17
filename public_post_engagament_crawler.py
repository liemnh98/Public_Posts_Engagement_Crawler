import pandas as pd
import time
import random
import re

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from seleniumwire import webdriver as sw_webdriver
from bs4 import BeautifulSoup

# Input/output paths
input_path = 'data/input_demo.csv'
output_path = 'data/output_demo.csv'
chrome_path = 'chromedriver-win64/chromedriver.exe'

def init_chrome_driver(chrome_path=chrome_path):
    options = webdriver.ChromeOptions()
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36')
    options.add_argument('log-level=3')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    service = Service(executable_path=chrome_path)
    driver = sw_webdriver.Chrome(service=service, options=options)
    return driver

def fb_reel(soup):
    """Extract like, comment, share for Facebook Reels using icon and value positions."""
    reel_span_class = 'x1lliihq x6ikm8r x10wlt62 x1n2onr6 xlyipyv xuxw1ft x1j85h84'
    icon_class = 'x1b0d499 xep6ejk'
    tags = list(soup.find_all(True))
    # Find icon positions
    icon_indices = [
        i for i, tag in enumerate(tags)
        if tag.name == 'i' and tag.get('class') and ' '.join(tag.get('class')) == icon_class
    ]
    # Find value positions
    value_indices = [
        (i, tag.get_text(strip=True))
        for i, tag in enumerate(tags)
        if tag.name == 'span' and tag.get('class') and ' '.join(tag.get('class')) == reel_span_class
    ]
    # For each icon, get the first value after this icon and before the next icon
    values = []
    for idx, icon_idx in enumerate(icon_indices):
        next_icon_idx = icon_indices[idx + 1] if idx + 1 < len(icon_indices) else len(tags)
        value = ''
        for val_idx, val_text in value_indices:
            if icon_idx < val_idx < next_icon_idx:
                value = val_text
                break
        values.append(value)
    tmp_like = values[0]
    tmp_comment = values[1]
    tmp_share = values[2]
    return tmp_like, tmp_comment, tmp_share

def fb_broad(soup):
    """Extract like, comment, share for standard Facebook posts."""
    tmp_like, tmp_comment, tmp_share = '', '', ''
    main_div = soup.find('div', class_='x1n2onr6')
    if main_div:
        like_spans = main_div.find_all('span', class_='x135b78x')
        if like_spans:
            tmp_like = like_spans[-1].get_text(strip=True)
        html_span_class = 'html-span xdj266r x14z9mp xat24cr x1lziwak xexx8yu xyri2b x18d9i69 x1c1uobl x1hl2dhg x16tdsg8 x1vvkbs xkrqix3 x1sur9pj'
        html_spans = main_div.find_all('span', class_= lambda c: c == html_span_class)
        for s in html_spans:
            text = s.get_text(strip=True)
            text_lower = text.lower()
            if 'comment' in text_lower:
                tmp_comment = text
            elif 'share' in text_lower:
                tmp_share = text
    return tmp_like, tmp_comment, tmp_share

def process_link(driver, link):
    driver.get(link)
    time.sleep(random.uniform(3, 5))
    soup = BeautifulSoup(driver.page_source, 'html5lib')
    if link.startswith('https://www.facebook.com/reel/'):
        tmp_like, tmp_comment, tmp_share = fb_reel(soup)
    else:
        tmp_like, tmp_comment, tmp_share = fb_broad(soup)
    ldp = driver.current_url
    return {
        'link': link,
        'like': tmp_like,
        'comment': tmp_comment,
        'share': tmp_share,
        'ldp': ldp
    }

def parse_number(text):
    if pd.isnull(text):
        return 0
    text = str(text)
    match = re.search(r'([\d,.]+)([KkMm]?)', text.replace(',', ''))
    if not match:
        return 0
    num, suffix = match.groups()
    num = float(num)
    if suffix.lower() == 'k':
        num *= 1_000
    elif suffix.lower() == 'm':
        num *= 1_000_000
    return int(num)

def main():
    urls = pd.read_csv(input_path, encoding='utf-8', header=0, usecols=['link_aired'])
    urls = urls[urls['link_aired'].str.contains('facebook.com', na=False)]
    driver = init_chrome_driver()
    results = []
    total = len(urls)
    success_count = 0
    error_count = 0
    bar_len = 50
    print(f"Total links to process: {total}")
    for idx, row in urls.iterrows():
        link = row['link_aired']
        try:
            res = process_link(driver, link)
            res['success'] = True
            success_count += 1
        except Exception as e:
            res = {'link': link, 'success': False, 'error': str(e)}
            error_count += 1
        results.append(res)
        percent = (idx + 1) / total
        filled_len = int(bar_len * percent)
        bar = '=' * filled_len + '-' * (bar_len - filled_len)
        print(
            f"[{bar}] {percent:.0%} | {idx+1}/{total} | Success: {success_count} | Error: {error_count}",
            end='\r'
        )
    print()  # Newline after progress
    driver.quit()
    df_results = pd.DataFrame(results)
    df_results['like_num'] = df_results['like'].apply(parse_number)
    df_results['comment_num'] = df_results['comment'].apply(parse_number)
    df_results['share_num'] = df_results['share'].apply(parse_number)
    df_results[[
        'link', 'like_num', 'comment_num', 'share_num', 'ldp', 'success'
        ]].to_csv(output_path, index=False, encoding='utf-8')

if __name__ == '__main__':
    main()
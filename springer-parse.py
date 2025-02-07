import requests
from bs4 import BeautifulSoup, Tag
from tqdm import tqdm
import pandas as pd

BASE_URL = "https://link.springer.com"
SEARCH_URL = BASE_URL + "/search"
KEYWORDS = [
    "Non-financial reporting",
    "Sustainability reporting",
    "Integrated reporting",
    "ESG reporting",
    "Ecological reporting",
    "Social Responsibility reporting"
]
FILTER_LANGUAGE = "&facet-language=En"
PREMIUM_FILTER = "&showAll=true"
RECORDS_PER_PAGE = 20

session = requests.Session()


def get_max_page_and_results(query):
    url = f"{SEARCH_URL}{query}{FILTER_LANGUAGE}{PREMIUM_FILTER}"
    try:
        response = session.get(url, timeout=30)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"[ERROR] Failed to fetch {url} ({e})")
        return 0, 0

    soup = BeautifulSoup(response.text, "html.parser")

    max_page_span = soup.find("span", class_="number-of-pages")
    if not max_page_span or not max_page_span.text.strip().isdigit():
        print("[WARNING] Could not find or parse the total number of pages. Defaulting to 1 page.")
        max_pages = 1
    else:
        max_pages = int(max_page_span.text.strip())
    print(f"[OK] {max_pages} pages found")

    results_count_h1 = soup.find("h1", id="number-of-search-results-and-search-terms")
    if not results_count_h1:
        results_count = 0
        print("[ERROR] No results found")
    else:
        results_count_text = results_count_h1.find("strong")
        if not results_count_text or not results_count_text.text.strip().replace(',', '').isdigit():
            results_count = 0
            print("[ERROR] No results found")
        else:
            results_count = int(results_count_text.text.strip().replace(',', ''))
    print(f"[OK] {results_count} results found")
    return max_pages, results_count


def parse_search_results(url):
    try:
        response = session.get(url, timeout=30)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"[ERROR] Failed to fetch {url} ({e})")
        return []

    print(f"\t[DEBUG] Fetched URL: {url}")
    soup = BeautifulSoup(response.text, "html.parser")
    records = soup.find_all("a", class_="title")
    return records


def extract_country(country_str):
    parts = country_str.split(',')
    return parts[-1].strip() if parts else country_str.strip()


def extract_year(year_str):
    parts = year_str.split()
    return parts[-1] if parts else year_str.strip()


def parse_record_page(record):
    if not record.has_attr('href'):
        print("\t[ERROR] Record does not have href attribute. Skipping.")
        return None

    url = BASE_URL + record['href']
    try:
        response = session.get(url, timeout=30)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"\t[ERROR] Failed to fetch record page {url}: {e}")
        return None

    print(f"\t[DEBUG] Fetched record page: {url}")
    soup = BeautifulSoup(response.text, "html.parser")

    title_tag = soup.find("h1", class_="c-article-title")
    title = title_tag.text.strip() if title_tag else ""

    year = ""
    identifiers_ul = soup.find("ul", class_="c-article-identifiers")
    if identifiers_ul:
        time_tag = identifiers_ul.find("time")
        if time_tag:
            year = extract_year(time_tag.text.strip())

    type_tag = soup.select_one('nav[data-test="breadcrumbs"] li:last-child span[itemprop="name"]')
    article_type = type_tag.text.strip() if type_tag else ""

    extended_type_tag = soup.find('li', {'data-test': 'article-category'})
    extended_type = extended_type_tag.text.strip() if extended_type_tag else ""

    abstract_tag = soup.find("div", class_="c-article-section__content")
    abstract = abstract_tag.text.strip() if abstract_tag else ""

    country_tag = soup.find("p", class_="c-article-author-affiliation__address")
    country = extract_country(country_tag.text.strip()) if country_tag else ""

    return {
        'title': title,
        'year': year,
        'type': article_type,
        'extended_type': extended_type,
        'abstract': abstract,
        'country': country
    }


def process_keyword(keyword):
    print(f"\n[INFO] Processing keyword: '{keyword}'")
    query = f"?dc.title={keyword.replace(' ', '+')}"
    max_pages, results_count = get_max_page_and_results(query)
    if results_count == 0:
        print(f"[ERROR] No results found for keyword '{keyword}'.")
        return []

    records_list = []
    for page in range(1, max_pages + 1):
        page_url = f"{SEARCH_URL}/page/{page}{query}{FILTER_LANGUAGE}{PREMIUM_FILTER}"
        print(f"[LOG] Processing page {page}/{max_pages} for keyword '{keyword}': {page_url}")
        records = parse_search_results(page_url)
        if not records:
            print(f"[WARNING] No records found on page {page} for keyword '{keyword}'.")
            continue

        progress_bar = tqdm(records, desc=f"Processing records (Page {page})", unit="record", leave=False)
        for idx, item in enumerate(progress_bar):
            # Если по каким-то причинам item является кортежем, попробуем его распаковать
            if isinstance(item, tuple):
                # Если кортеж имеет два элемента, второй должен быть нужным тегом
                if len(item) == 2:
                    _, record = item
                else:
                    print(f"\t[WARNING] Unexpected tuple structure: {item}. Skipping.")
                    continue
            else:
                record = item

            # Дополнительная проверка, что record действительно является тегом BeautifulSoup
            if not isinstance(record, Tag):
                print(f"\t[WARNING] Skipping non-Tag record: {record}")
                continue

            try:
                text_content = record.text.strip()
            except Exception as e:
                print(f"\t[ERROR] Cannot retrieve text from record: {e}. Skipping.")
                continue

            print(f"\t[LOG] Parsing record {idx + 1}/{len(records)}: {text_content}")
            data = parse_record_page(record)
            if not data:
                print(f"\t[ERROR] Failed to parse record: {text_content}. Skipping.")
                continue
            records_list.append(data)
    return records_list


def main():
    results_by_keyword = {}
    for keyword in KEYWORDS:
        keyword_records = process_keyword(keyword)
        results_by_keyword[keyword] = keyword_records

    excel_filename = "springer_results.xlsx"
    with pd.ExcelWriter(excel_filename, engine="openpyxl") as writer:
        for keyword, records in results_by_keyword.items():
            if records:
                df = pd.DataFrame(records)
            else:
                df = pd.DataFrame(columns=['title', 'year', 'type', 'extended_type', 'abstract', 'country'])

            sheet_name = keyword if len(keyword) <= 31 else keyword[:31]
            df.to_excel(writer, sheet_name=sheet_name, index=False)
    print(f"\n[INFO] Data has been written to '{excel_filename}'")


if __name__ == "__main__":
    main()

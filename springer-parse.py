import requests
from bs4 import BeautifulSoup

BASE_URL = "https://link.springer.com"
SEARCH_URL = BASE_URL + "/search"
KEYWORDS = [
    "Non-financial reporting",
    # "Sustainability reporting",
    # "Integrated reporting",
    # "ESG reporting",
    # "Ecological reporting",
    # "Social Responsibility reporting"
]
FILTER_LANGUAGE = "&facet-language=En"
PREMIUM_FILTER = "&showAll=true"
RECORDS_PER_PAGE = 20


def get_max_page(query):
    url = f"{SEARCH_URL}{query}{FILTER_LANGUAGE}{PREMIUM_FILTER}"

    response = requests.get(url, timeout=30)
    if response.status_code != 200:
        print(f"[ERROR] {response.status_code} ({url})")
        return 0
    else:
        print(f"[DEBUG] {url}")

    soup = BeautifulSoup(response.text, "html.parser")
    max_page_span = soup.find("span", class_="number-of-pages")

    if not max_page_span:
        print("[ERROR] No pages found")
    else:
        print(f"[DEBUG] {max_page_span}")

    max_pages = int(max_page_span.text)
    print(f"[OK] {max_pages} pages found")

    results_count_h1 = soup.find("h1", id="number-of-search-results-and-search-terms")

    if not results_count_h1:
        print("[ERROR] No results found")
        return 0
    else:
        results_count_text = results_count_h1.find("strong")

        if not results_count_text:
            print("[ERROR] No results found")
        print(f"[DEBUG] {results_count_h1} -> {results_count_text}")

    results_count = int(results_count_text.text)
    print(f"[OK] {results_count} results found")

    return max_pages, results_count


def parse_old_springer_page(url):
    response = requests.get(url, timeout=30)
    if response.status_code != 200:
        print(f"\t[ERROR] {response.status_code} ({url})")
        return 0
    else:
        print(f"\t[DEBUG] {url}")

    soup = BeautifulSoup(response.text, "html.parser")
    cards = soup.find_all("a", class_="title")

    return cards


def parse_record_page(record):
    url = BASE_URL + record['href']
    response = requests.get(url, timeout=30)
    if response.status_code != 200:
        print(f"\t[ERROR] {response.status_code} ({url})")
        return 0
    else:
        print(f"\t[DEBUG] {url}")

    soup = BeautifulSoup(response.text, "html.parser")
    title = soup.find("h1", class_="ArticleTitle")
    authors = soup.find("a", class_="authors__name")
    year = soup.find("time", class_="ArticleCitation_Year")
    abstract = soup.find("div", class_="c-article-section__content")

    return {
        'title': title.text.strip() if title else "",
        'authors': authors.text.strip() if authors else "",
        'year': year.text.strip() if year else "",
        'abstract': abstract.text.strip() if abstract else ""
    }


def main():
    for keyword in KEYWORDS:
        query = f"?dc.title={keyword.replace(" ", "+")}"
        max_pages, results_count = get_max_page(query)

        for page in range(1, max_pages + 1):
            url = f"{SEARCH_URL}/page/{page}{query}{FILTER_LANGUAGE}{PREMIUM_FILTER}"
            print(f"[LOG] Parsing {page} page")

            records = parse_old_springer_page(url)
            if not records:
                print(f"[ERROR] No records")
                return

            for record in records:
                print(f"[DEBUG] {record}")
                print(f"\t[LOG] Parsing \"{record.text}\"")

                data = parse_record_page(record)
                if not data:
                    print(f"\t[ERROR] No data")
                    return
                else:
                    print(f"\t[OK] {data}")


if __name__ == "__main__":
    main()

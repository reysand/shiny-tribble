import requests

SPRINGER_API_KEY = "ad40e178710f1cc7447a0324f0396bc1"

KEYWORDS = [
    "Non-financial reporting",
    "Sustainability reporting",
    "Integrated reporting",
    "ESG reporting",
    "Ecological reporting",
    "Social Responsibility reporting"
]

LANGUAGE = [
    "En"
]

CONTENT_TYPES = [
    "Article",
    "Book",
    "Chapter",
    "Research",
    "Review",
    "Conference Paper"
]

BASE_URL = "https://api.springer.com/metadata/json"


def fetch_springer_data(query, page, page_size):
    params = {
        'api_key': SPRINGER_API_KEY,
        'q': query,
        'p': page,
        's': (page - 1) * page_size + 1
    }
    try:
        response = requests.get(BASE_URL, params=params, timeout=30)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Ошибка: код {response.status_code} при запросе {page} (query=\"{query}\").")
            return None
    except Exception as e:
        print(f"Ошибка при запросе {page} (query=\"{query}\"): {e}")
        return None

def parse_affiliation_country(affiliations):
    if not affiliations:
        return ""
    for aff in affiliations:
        parts = aff.strip().split()
        if parts:
            return parts[-1]
    return ""


def test(keyword: str, limit: int):
    data = fetch_springer_data(keyword, page=25, page_size=limit)
    if not data or 'records' not in data or len(data['records']) == 0:
        print(f"Нет данных для запроса {keyword}.")
        return

    print(f"Данные для запроса {keyword}:")

    print(data)

    print(f"==========================================================")
    for x in data['records']:

        record = x
        print(record)

        title = record.get('title', "")
        pub_year = record.get('publicationDate', "")[:4]
        content_type = record.get('contentType', "")
        abstract = record.get('abstract', "")

        all_affiliations = []
        if 'creators' in record:
            for c in record['creators']:
                aff = c.get('affiliation', [])
                if aff:
                    all_affiliations.extend(aff)
        country = parse_affiliation_country(all_affiliations)

        print("==========================================================")
        print(f"Title: {title}")
        print(f"Publication Year: {pub_year}")
        print(f"Publication Type: {content_type}")
        print(f"Abstract: {abstract[:200]}{'...' if len(abstract) > 200 else ''}")  # Обрезаем для вывода
        print("==========================================================")


if __name__ == "__main__":
    # main()
    test("Ecological reporting", 25)
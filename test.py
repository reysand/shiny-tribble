# import requests
# import time
# import openpyxl
# from openpyxl.utils import get_column_letter
# import re
# from bs4 import BeautifulSoup
#
# def parse_springer_page(url):
#     """
#     Делает GET-запрос к заданному url, ищет на странице блоки публикаций,
#     извлекает нужные поля и возвращает список словарей:
#     [
#       {
#         "type": "...",
#         "title": "...",
#         "link": "...",
#         "annotation": "...",
#         "authors": "...",
#         "year": "...",
#       },
#       ...
#     ]
#     """
#     r = requests.get(url, timeout=30)
#     if r.status_code != 200:
#         print(f"Ошибка {r.status_code} при запросе {url}")
#         return []
#
#     soup = BeautifulSoup(r.text, "html.parser")
#     results = []
#
#     # По вашему описанию, каждая карточка статьи находится в <div class="app-card-open__main">
#     cards = soup.find_all("div", class_="app-card-open__main")
#     if not cards:
#         # Возможно, нужно проверить альтернативную структуру, если что-то поменялось
#         print(f"Не найдено блоков .app-card-open__main на {url}")
#         return []
#
#     for card in cards:
#         # тип (напр. Article, Chapter и т.д.) в <span class="c-meta__type">
#         span_type = card.find("span", class_="c-meta__type")
#         pub_type = span_type.get_text(strip=True) if span_type else ""
#
#         # ссылка + название: <a class="app-card-open__link" href="...">
#         link_elem = card.find("a", class_="app-card-open__link")
#         if link_elem:
#             href = link_elem.get("href", "")
#             if href.startswith("/"):
#                 full_link = "https://link.springer.com" + href
#             else:
#                 full_link = href
#             title = link_elem.get_text(strip=True)
#         else:
#             full_link = ""
#             title = ""
#
#         # короткая аннотация: <div class="app-card-open__description"><p>...</p></div>
#         annotation_div = card.find("div", class_="app-card-open__description")
#         annotation = ""
#         if annotation_div:
#             p = annotation_div.find("p")
#             if p:
#                 annotation = p.get_text(strip=True)
#
#         # авторы: <div class="c-author-list c-author-list--truncated c-author-list--compact">
#         author_div = card.find("div", class_="c-author-list c-author-list--truncated c-author-list--compact")
#         authors = author_div.get_text(strip=True) if author_div else ""
#
#         # год из даты: <span class="c-meta__item" data-test="published">...</span>
#         date_span = card.find("span", class_="c-meta__item", attrs={"data-test": "published"})
#         pub_year = ""
#         if date_span:
#             date_str = date_span.get_text(strip=True)
#             # Найдём год (упрощённо)
#             match = re.search(r'(19|20)\d{2}', date_str)
#             if match:
#                 pub_year = match.group(0)
#
#         # Формируем результат
#         results.append({
#             "type": pub_type,
#             "title": title,
#             "link": full_link,
#             "annotation": annotation,
#             "authors": authors,
#             "year": pub_year
#         })
#
#     return results
#
#
# def main():
#     # Подготовка Excel
#     wb = openpyxl.Workbook()
#     ws = wb.active
#     ws.title = "SpringerParsed"
#
#     # Названия столбцов
#     headers = ["Type", "Title", "Link", "Annotation", "Authors", "Year"]
#     for col_index, header in enumerate(headers, start=1):
#         ws.cell(row=1, column=col_index, value=header)
#         ws.column_dimensions[get_column_letter(col_index)].width = 40
#
#     row_counter = 2
#
#     # Базовая ссылка:
#     # По вашему примеру:
#     base_url = (
#         "https://link.springer.com/search?new-search=true"
#         "&query=%22Ecological+reporting%22"
#         "&content-type=article&content-type=research&content-type=chapter"
#         "&content-type=conference+paper&content-type=review&content-type=book"
#         "&dateFrom=&dateTo="
#         "&language=En"
#         "&sortBy=relevance"
#     )
#
#     for page_num in range(1, 11):
#         # Добавляем параметр &page=N
#         url = f"{base_url}&page={page_num}"
#         print(f"Парсим страницу: {url}")
#         records = parse_springer_page(url)
#         if not records:
#             print(f"На странице {page_num} результатов не найдено, завершаем.")
#             break
#
#         # Запись в Excel
#         for rec in records:
#             ws.cell(row=row_counter, column=1, value=rec["type"])
#             ws.cell(row=row_counter, column=2, value=rec["title"])
#             ws.cell(row=row_counter, column=3, value=rec["link"])
#             ws.cell(row=row_counter, column=4, value=rec["annotation"])
#             ws.cell(row=row_counter, column=5, value=rec["authors"])
#             ws.cell(row=row_counter, column=6, value=rec["year"])
#             row_counter += 1
#
#         # Сохраняем промежуточно
#         wb.save("springer_parsed.xlsx")
#
#         # Задержка, чтобы не спамить сайт
#         time.sleep(1)
#
#     print("Готово! Итог в springer_parsed.xlsx")
#
#
# if __name__ == "__main__":
#     main()

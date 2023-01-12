# ADPY62
# Домашнее задание к лекции «Web-scrapping»
# получать интересующие нас статьи на хабре (https://habr.com/)

# Необходимо парсить страницу со свежими статьями (вот эту: https://habr.com/ru/all/)
# и выбирать те статьи, в которых встречается хотя бы одно из ключевых слов (эти слова определяем в начале скрипта).
# Поиск вести по всей доступной preview-информации (это информация, доступная непосредственно с текущей страницы).
# Вывести в консоль список подходящих статей в формате: <дата> - <заголовок> - <ссылка>.

import requests
from fake_headers import Headers
import bs4
from pprint import pprint

if __name__ == '__main__':
    URL = 'https://habr.com'
    PATH = '/ru/all/'
    KEYWORDS = ['дизайн', 'фото', 'web', 'python']
    HEADERS = Headers(os="win", browser='chrome', headers=True).generate()  # подставной заголовок от fake_headers

    response = requests.get(url=URL + PATH, headers=HEADERS)
    text = response.text
    soup = bs4.BeautifulSoup(text, features='html.parser')
    articles = soup.find_all('article')

    print(f'\nИщем подходящие статьи из {len(articles)} статей на странице {URL}{PATH},\n'
          f'в которых встречаются слова/фразы из списка:\t{KEYWORDS}\n')
    result_articles = []

    for article in articles:
        title = article.find(class_='tm-article-snippet__title-link')
        author = article.find(class_='tm-user-info__username')
        preview = article.find(class_='article-formatted-body').find_all('p')
        article_info = {
            'article_id': article['id'],
            'article_href': URL + title["href"],
            'article_title': title.find("span").text.strip(),
            'author_href': author["href"],
            'author_username': author.text.strip(),
            'hubs_text': article.find_all(class_='tm-article-snippet__hubs')[0].text.strip(),
            'hubs_list': [{'href': hub["href"], 'title': hub.find("span").text.strip()}
                          for hub in article.find_all(class_='tm-article-snippet__hubs-item-link')],
            'datetime_string': article.find(class_='tm-article-snippet__datetime-published'
                                            ).find('time')['title'].strip(),
            'preview': ''.join(p.text for p in preview)
        }

        # --> Весь текст превью:
        preview_text = "{} {} {}".format(
            article_info['article_title'], article_info['hubs_text'], article_info['preview'])
        # print(f"\n ПРЕВЬЮ статьи {article_info['article_title']} --> {article_info['article_href']})\n")
        # pprint(preview_text)  # -------------------------------

        # --> Страница с проверяемой статьёй:
        article_page_response = requests.get(url=article_info['article_href'], headers=HEADERS)
        article_page = bs4.BeautifulSoup(article_page_response.text, features='html.parser')
        full_article = article_page.find('article').find(class_='article-formatted-body')
        full_text = ''.join(tag.text.strip() for tag in full_article.find_all(['p', 'h3', 'h4']))
        # print(f"\n ПОЛНЫЙ ТЕКСТ статьи {article_info['article_title']} --> {article_info['article_href']})\n")
        # pprint(full_text)  # -------------------------------

        for keyword in KEYWORDS:
            if (keyword in preview_text) or (keyword in full_text):
                article_info['text'] = full_text
                result_articles.append(article_info)
                print('\t',  # <дата> - <заголовок> - <ссылка>
                      article_info['datetime_string'].split(',', 1)[0], '-',
                      article_info['article_title'], '-',
                      f' (найдено слово "{keyword}") -',
                      article_info['article_href'])
                break

    print(f'\nНайдено {len(result_articles)} подходящих статей')

import re
import requests
from bs4 import BeautifulSoup


def get_page(url):
    response = requests.get(url)
    return response.text


# Make list of some data like genre, actors. Made for get rid of redundancy
def list_maker(data):
    if len(data) > 1:
        for i in range(len(data)):
            data[i] = data[i].text
    else:
        data[0] = data[0].text
    return data


# Scrape wikipedia
def fetch_data(page_text):
    soup = BeautifulSoup(page_text, 'lxml')
    movie_info = soup.find('table', class_='infobox vevent')
    all_info = movie_info.find_all('tr')
    if movie_info.get('data-name') is None:
        en_name = all_info[0].text
        year_raw = movie_info.find('th', text='Release date').parent
        year = year_raw.find('li').find(text=True)
        director = list_maker(movie_info.find('th', text='Directed by').find_next_sibling().find_all('a'))
        stars = list_maker(movie_info.find('th', text='Starring').parent.find_all('li'))
        movie_dict = {'eng_name': en_name, 'year': year, 'director': director, 'stars': stars}
    else:
        ru_name = all_info[0].text
        en_name = all_info[1].text
        genre_raw = movie_info.find(text='Жанр').parent.parent.parent
        genre = list_maker(genre_raw.find('span').find_all('a'))
        year = movie_info.find('th', text='Год').find_next_sibling().text.strip()
        director = list_maker(movie_info.find('th', text='Режиссёр').find_next_sibling().find_all('a'))
        stars = []
        for span in all_info:
            if span.find(text=re.compile('В главных')):
                stars = list_maker(span.find_all('a'))
        movie_dict = {'ru_name': ru_name, 'eng_name': en_name, 'year': year,
                      'director': director, 'stars': stars, 'genres': genre}
    return movie_dict


def main():
    url = input()
    page_text = get_page(url)
    fetch_data(page_text)


if __name__ == '__main__':
    main()
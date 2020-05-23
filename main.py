import re
import csv
import requests
from bs4 import BeautifulSoup


# Get html text from website
# Return html text for parsing
def get_page(url):
    response = requests.get(url)
    return response.text


# Writing parsed data into csv file
# This functoin add  comma separator
# If there is more that 1 genre, director and star
def write_csv(data):
    with open('movies.csv', 'a', encoding='utf-8', newline='') as file:
        writer = csv.writer(file)
        data['director'] = ', '.join(data.get('director', ''))
        data['genres'] = ', '.join(data.get('genres', ''))
        data['stars'] = ', '.join(data.get('stars', ''))
        writer.writerow((data.get('ru_name', ''), data.get('eng_name', ''),
                         data.get('year', ''), data.get('director', ''),
                         data.get('stars', ''), data.get('genres', '')))
        print(data.get('ru_name'))
        print(data.get('eng_name'))
        print('Write OK')


# Remove useless info from list, such as commas, \n, space, and empty 
def polish_remover(data):
    new_data = []
    print(data)
    for i in range(len(data)):
        data[i] = data[i].replace('\n', '')
        if len(data[i]) > 2:
            new_data.append(data[i])
    print(data)
    print(new_data)
    return new_data


# Search for directors, since it's same for eng and ru
# We can write it in one place instead of two
def director_list(movie_info, dir_lang):
    directors_raw_text = movie_info.find('th', text=dir_lang)
    directors_list = directors_raw_text.find_next_sibling().find_all(text=True)
    return polish_remover(directors_list)


# Scrape wikipedia for our info and put this info in dict of lists
# Would like to revrite repeats like with director_list function
def fetch_data(page_text):
    soup = BeautifulSoup(page_text, 'lxml')
    movie_info = soup.find('table', class_='infobox vevent')
    all_info = movie_info.find_all('tr')
    stars = []
    dir_lang = ['Directed by', 'Режиссёр']
    if movie_info.get('data-name') is None:
        en_name = all_info[0].text
        year_raw = movie_info.find('th', text='Release date').parent
        year = year_raw.find('li').find(text=True)
        directors = director_list(movie_info, dir_lang[0])
        stars_list = movie_info.find('th', text='Starring').parent.find_all(text=True)
        stars = polish_remover(stars_list)[1:]
        movie_dict = {'eng_name': en_name, 'year': year,
                      'director': directors, 'stars': stars}
    else:
        ru_name = all_info[0].text
        en_name = all_info[1].text
        genre_raw = movie_info.find(text='Жанр').parent.parent.parent
        genre_list = genre_raw.find('span').find_all(text=True)
        year = movie_info.find('th', text='Год').find_next_sibling().text.strip()
        directors = director_list(movie_info, dir_lang[1])
        genre = polish_remover(genre_list)
        stars_list = movie_info.find(text=re.compile('В главных'))
        if stars_list is not None:  # feels like you could make it simplier
            stars = polish_remover(stars_list.parent.parent.find_all(text=True))[2:]
        movie_dict = {'ru_name': ru_name, 'eng_name': en_name, 'year': year,
                      'director': directors, 'stars': stars, 'genres': genre}
    return movie_dict


# Just run loop and wait for link from user
def main():
    while True:
        print('Paste Wiki page link of movie')
        url = input()
        page_text = get_page(url)
        data = fetch_data(page_text)
        write_csv(data)


if __name__ == '__main__':
    main()

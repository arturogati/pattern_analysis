import requests
from bs4 import BeautifulSoup

# URL страницы
url = "https://www.tradingview.com/symbols/10000LADYSUSDT.P/technicals/"

# Заголовки для имитации запроса от браузера
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
}

# Отправка GET-запроса
response = requests.get(url, headers=headers)

# Проверка успешности запроса
if response.status_code == 200:
    # Парсинг HTML-контента
    soup = BeautifulSoup(response.text, 'html.parser')
    print(soup)
    
    # Поиск контейнера с оценками
    container = soup.find('div', class_='container-vLbFM67a container-buy-vLbFM67a container-large-vLbFM67a')
    
    if container:
        # Поиск активной оценки (видимой на странице)
        active_rating = container.find('span', class_='text-large-vLbFM67a', attrs={'style': ''})  # Активный элемент обычно не имеет стиля скрытия
        if not active_rating:
            # Если активный элемент не найден по стилю, ищем по классу strong-buy, strong-sell и т.д.
            active_rating = container.find('span', class_=lambda x: x and ('strong-buy' in x or 'strong-sell' in x or 'buy' in x or 'sell' in x or 'neutral' in x))
        
        if active_rating:
            print("Общая оценка:", active_rating.text.strip())
        else:
            print("Не удалось найти активную оценку в контейнере.")
    else:
        print("Не удалось найти контейнер с оценками на странице.")
else:
    print("Не удалось загрузить страницу. Код статуса:", response.status_code)
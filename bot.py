import requests
from bs4 import BeautifulSoup
import os

# Отримуємо наші таємні ключі з налаштувань GitHub
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')

def send_message(text):
    """Функція для відправки повідомлення в Telegram"""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": text, "parse_mode": "HTML"}
    requests.post(url, json=payload)

def main():
    url = "https://www.gate.com/uk/launchpool"
    # Прикидаємось звичайним браузером, щоб сайт нас не заблокував
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        # Завантажуємо сторінку
        response = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Хитрий крок: збираємо тільки заголовки на сторінці (де зазвичай лежать назви проектів). 
        # Це захищає нас від помилкових спрацьовувань через зміну цін або таймерів.
        titles = []
        for tag in soup.find_all(['h1', 'h2', 'h3', 'h4']):
            text = tag.get_text(strip=True)
            if text:
                titles.append(text)
                
        # Об'єднуємо всі знайдені заголовки в один великий текст
        current_state = "\n".join(titles)
        
        # Читаємо, які проекти бот бачив минулого разу
        last_state = ""
        if os.path.exists("last_state.txt"):
            with open("last_state.txt", "r", encoding="utf-8") as f:
                last_state = f.read()
            
        # Якщо є зміни (з'явився новий проект) і це не перший запуск
        if current_state != last_state and current_state != "":
            if last_state != "":
                msg = f"🚀 <b>Увага! На Gate.io Launchpool відбулися зміни!</b>\n\nМожливо, з'явився новий проект.\n👉 Перевір сайт: {url}"
                send_message(msg)
                
            # Запам'ятовуємо новий стан (записуємо у файл)
            with open("last_state.txt", "w", encoding="utf-8") as f:
                f.write(current_state)
                
    except Exception as e:
        print(f"Сталася помилка при перевірці: {e}")

if __name__ == "__main__":
    main()

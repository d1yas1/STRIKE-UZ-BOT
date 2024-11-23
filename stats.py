from datetime import datetime
from databace import cursor, connect
from config import GROUP_IDS
import requests
from bs4 import BeautifulSoup
import asyncio


async def fetch_server_statistics():
    url = 'http://strike.uz'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    elements = soup.find_all('td')
    data = [element.text.strip() for element in elements]
    filtered_data = [d for d in data if isinstance(d, str)]

    total_online = 0
    total_capacity = 0
    for count, i in enumerate(filtered_data):
        if 'Strike.Uz' in i or 'YouTube' in i:
            players_data = filtered_data[count + 1]
            current_players, max_capacity = map(int, players_data.split(' из '))
            total_online += current_players
            total_capacity += max_capacity

    overall_percentage = (total_online / total_capacity) * 100 if total_capacity > 0 else 0
    return total_online, total_capacity, overall_percentage


async def save_and_send_statistics(group_ids, bot):
    total_online, total_capacity, overall_percentage = await fetch_server_statistics()
    overall_percentage = round(overall_percentage, 1)
    timestamp = datetime.now().strftime("%d/%m/%Y %H:%M")
    cursor.execute("SELECT record FROM stats WHERE id = 1")
    result = cursor.fetchone()
    if result is None:
        cursor.execute("INSERT INTO stats (id, record) VALUES (1, ?)", (overall_percentage,))
        connect.commit()
    elif overall_percentage > result[0]:
        cursor.execute("UPDATE stats SET record = ? WHERE id = 1", (overall_percentage,))
        connect.commit()
        for group_id in group_ids:
            message = f"""<b>😱 New Record 😱

🇺🇿 Strike.Uz [sana: {timestamp}] da online bo'yicha yangi rekordni o'rnatdi: {total_online}/{total_capacity} [{overall_percentage:.1f}%]🔥

🇷🇺 Strike.Uz установил новый рекорд в [sana: {timestamp}] по количеству онлайна: {total_online}/{total_capacity} [{overall_percentage:.1f}%]🔥
</b>"""
            await bot.send_message(group_id, message, parse_mode="HTML")


async def periodic_statistics(bot):
    while True:
        await save_and_send_statistics(GROUP_IDS, bot)
        await asyncio.sleep(15)
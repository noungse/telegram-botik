import asyncio
import logging
import feedparser
import pyshorteners
import random
from datetime import datetime
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

logging.basicConfig(level=logging.INFO)
import os
API_TOKEN = os.getenv('TELEGRAM_TOKEN')

bot = Bot(token=API_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()


subscribers = set()
shortener = pyshorteners.Shortener()

# кнопочки
game_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📰 Новости"), KeyboardButton(text="🎲 Случайная игра")],
        [KeyboardButton(text="🔔 Подписаться"), KeyboardButton(text="📊 Подписчики")],
        [KeyboardButton(text="❓ Помощь")]
    ],
    resize_keyboard=True,
    input_field_placeholder="Нажми кнопку..."
)

#ссылки на новости
RSS_URLS = [
    'https://stopgame.ru/rss/all.xml',
    'https://www.igromania.ru/rss/news.xml',
    'https://dtf.ru/rss/all',
]

def get_gaming_news(limit=10):
    all_news = []
    for url in RSS_URLS:
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:3]:
                title = entry.title
                link = entry.link
                try:
                    short_link = shortener.clckru.short(link)
                except:
                    short_link = link
                
                source = url.split('.')[1].upper()
                news_item = f"🎮 [{source}] <b>{title}</b>\n{short_link}"
                all_news.append(news_item)
        except Exception as e:
            print(f"Ошибка с {url}: {e}")
    return all_news[:limit]

#подписка на новости
async def send_news_to_subscribers():
    if not subscribers:
        print(f"[{datetime.now().strftime('%H:%M')}] Нет подписчиков")
        return
    
    print(f"[{datetime.now().strftime('%H:%M')}] Рассылка для {len(subscribers)} подписчиков...")
    
    news = get_gaming_news(limit=8)
    if not news:
        print("Новостей не найдено")
        return
    
    message_text = f"📰 <b>Игровые новости:</b>\n\n" + "\n\n".join(news)
    
    for user_id in subscribers:
        try:
            await bot.send_message(user_id, message_text)
            await asyncio.sleep(0.1)
        except Exception as e:
            print(f"Ошибка отправки {user_id}: {e}")
            if "bot was blocked" in str(e):
                subscribers.discard(user_id)
    
    print(f"[{datetime.now().strftime('%H:%M')}] Рассылка завершена")


async def scheduler():
    print("⏰ Планировщик запущен!")
    
    while True:
        now = datetime.now().strftime("%H:%M")
        
        if now == "09:00" or now == "18:00":
            await send_news_to_subscribers()
            await asyncio.sleep(60) 
        
        await asyncio.sleep(30)  

# команды
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        "🎮 <b>Привет! Я GameSage — бот с игровыми новостями!</b>\n\n"
        "Используй кнопки ниже:\n"
        "📰 Новости - свежие игровые новости\n"
        "🎲 Случайная игра - рекомендация игры\n"
        "🔔 Подписаться - ежедневная рассылка в 9:00 и 18:00\n"
        "📊 Подписчики - статистика\n"
        "❓ Помощь - справка",
        reply_markup=game_keyboard
    )

@dp.message(lambda message: message.text == "📰 Новости")
async def handle_news_button(message: types.Message):
    await cmd_news(message)

@dp.message(lambda message: message.text == "🎲 Случайная игра")
async def handle_random_button(message: types.Message):
    await cmd_random(message)

@dp.message(lambda message: message.text == "🔔 Подписаться")
async def handle_subscribe_button(message: types.Message):
    await cmd_subscribe(message)

@dp.message(lambda message: message.text == "📊 Подписчики")
async def handle_subscribers_button(message: types.Message):
    await cmd_subscribers(message)

@dp.message(lambda message: message.text == "❓ Помощь")
async def handle_help_button(message: types.Message):
    await cmd_help(message)

@dp.message(Command("news"))
async def cmd_news(message: types.Message):
    await message.answer("⏳ Ищу новости...")
    
    news = get_gaming_news(limit=10)
    
    if not news:
        await message.answer("😔 Новостей не найдено", reply_markup=game_keyboard)
        return
    
    message_text = "📰 <b>Игровые новости:</b>\n\n" + "\n\n".join(news)
    await message.answer(message_text, reply_markup=game_keyboard)

@dp.message(Command("random"))
async def cmd_random(message: types.Message):
    games = [
              
        "🎮 <b>Minecraft</b> - бесконечный мир для творчества и выживания",
        "⚔️ <b>The Witcher 3: Wild Hunt</b> - эпичное фэнтези с моральными выборами",
        "🌀 <b>Portal 2</b> - гениальные головоломки с порталами и чёрным юмором",
        "🔫 <b>Half-Life 2</b> - культовый шутер с физикой и сюжетом",
        "🏆 <b>Dark Souls</b> - сложный, но справедливый экшен-RPG",
        "🌾 <b>Stardew Valley</b> - уютная ферма, рыбалка и отношения с жителями",
        "⚔️ <b>Hades</b> - греческий рогалик с божественной прокачкой",
        "🦇 <b>Hollow Knight</b> - атмосферный метроидвания в мире насекомых",
        "🏆 <b>Celeste</b> - сложный, но вдохновляющий платформер",
        "🎨 <b>Disco Elysium</b> - детектив-RPG без боев, только диалоги",
        "⛏️ <b>Terraria</b> - 2D песочница с крафтом и битвами с боссами",
        "🔍 <b>Return of the Obra Dinn</b> - детектив про загадочный корабль",
        "👻 <b>Among Us</b> - сабвейер с предателем (лучше с друзьями!)",
        "🎭 <b>Baldur's Gate 3</b> - глубокая D&D RPG с тактическими боями",
        "🐉 <b>Elden Ring</b> - огромный open-world от создателей Dark Souls",
        "🌍 <b>Red Dead Redemption 2</b> - ковбойская сага про честь и выживание",
        "🔫 <b>Cyberpunk 2077</b> - неоновый киберпанк с Киану Ривзом",
        "🎮 <b>God of War (2018)</b> - скандинавская сага про Кратоса и Атрея",
        "🏰 <b>The Legend of Zelda: Breath of the Wild</b> - свобода исследований",
        "🚀 <b>Mass Effect Legendary Edition</b> - космическая опера с выборами",
        "🔫 <b>Counter-Strike 2</b> - тактический шутер про спецназ и террористов",
        "⚔️ <b>Dota 2</b> - сложная MOBA с сотнями героев",
        "🏆 <b>League of Legends</b> - популярная MOBA с регулярными обновлениями",
        "🎮 <b>Valorant</b> - тактический шутер со способностями персонажей",
        "🔫 <b>Overwatch 2</b> - динамичный геройский шутер",
        "👥 <b>Deep Rock Galactic</b> - кооператив про гномов-шахтеров",
        "🌌 <b>No Man's Sky</b> - исследование бесконечной вселенной",
        "✈️ <b>Microsoft Flight Simulator</b> - невероятно реалистичные полёты",
        "🚜 <b>Farming Simulator 22</b> - детальная симуляция фермы",
        "🎣 <b>Animal Crossing: New Horizons</b> - уютный островной рай",
        "🏞️ <b>Firewatch</b> - интерактивная драма в лесу",
        "👑 <b>Civilization VI</b> - построй свою империю от каменного века",
        "⚔️ <b>XCOM 2</b> - тактическая стратегия про войну с пришельцами",
        "🛡️ <b>Total War: Warhammer III</b> - грандиозные сражения в фэнтези-мире",
        "🌌 <b>Outer Wilds</b> - космическая археология в тайм-лупе",
        "🎭 <b>Undertale</b> - можно пройти без убийств (или с ними)",
        "🧩 <b>Baba Is You</b> - головоломка где правила можно менять",
        "🎵 <b>Beat Saber</b> - режь кубы под музыку в VR",
     ]
    
    random_game = random.choice(games)
    await message.answer(
        f"🎲 <b>Случайная игра:</b>\n\n{random_game}",
        reply_markup=game_keyboard
    )

@dp.message(Command("subscribe"))
async def cmd_subscribe(message: types.Message):
    user_id = message.from_user.id
    
    if user_id in subscribers:
        await message.answer("✅ Вы уже подписаны!", reply_markup=game_keyboard)
    else:
        subscribers.add(user_id)
        await message.answer("🎉 Вы подписались на рассылку!", reply_markup=game_keyboard)

@dp.message(Command("unsubscribe"))
async def cmd_unsubscribe(message: types.Message):
    user_id = message.from_user.id
    
    if user_id in subscribers:
        subscribers.discard(user_id)
        await message.answer("🔕 Вы отписались", reply_markup=game_keyboard)
    else:
        await message.answer("ℹ️ Вы не были подписаны", reply_markup=game_keyboard)

@dp.message(Command("subscribers"))
async def cmd_subscribers(message: types.Message):
    await message.answer(
        f"📊 Подписчиков: <b>{len(subscribers)}</b>",
        reply_markup=game_keyboard
    )

@dp.message(Command("help"))
async def cmd_help(message: types.Message):
    await message.answer(
        "🎮 <b>GameSage - помощник в мире игр!</b>\n\n"
        "Команды:\n"
        "/start - начать\n"
        "/news - новости\n"
        "/random - случайная игра\n"
        "/subscribe - подписаться\n"
        "/unsubscribe - отписаться\n"
        "/subscribers - статистика\n"
        "/help - справка\n\n"
        "Рассылка в 9:00 и 18:00",
        reply_markup=game_keyboard
    )

#запускаем машину
async def main():
    print("🎮 GameSage запускается...")
    
    asyncio.create_task(scheduler())
    
    print(" Бот готов!")
    await dp.start_polling(bot)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n Бот остановлен")
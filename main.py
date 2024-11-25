import json
import asyncio
from pyrogram import Client
from pyrogram.errors import RPCError, MsgIdInvalid, FloodWait
from pyrogram.raw.functions.messages import GetMessageReactionsList

# Ваши API ID и API Hash (получите их на https://my.telegram.org)
api_id = 123456  # Замените на ваш API ID
api_hash = "your_api_hash"  # Замените на ваш API Hash

# Конфигурация
channel_username = "your_channel_username"  # Замените на username канала/группы
limit = 100  # Количество сообщений для сканирования
delay = 1  # Задержка между запросами (в секундах)
user_file = 'users.json'  # Файл для сохранения данных пользователей

# Инициализация Pyrogram клиента
app = Client("my_account", api_id=api_id, api_hash=api_hash)

async def get_reactions(client, chat, message_id):
    """
    Получает список пользователей, которые оставили реакции на сообщение.
    Работает только для групп и супергрупп.
    """
    user_ids = set()
    try:
        # Получаем "peer" для чата
        r_peer = await client.resolve_peer(chat)
        # Получаем список реакций
        reactions = await client.invoke(GetMessageReactionsList(peer=r_peer, id=message_id, limit=-1))

        # Добавляем ID пользователей, оставивших реакции
        for reaction in reactions.reactions:
            for reactor in reaction.users:
                user_ids.add(reactor.user_id)
                print(f"Добавлен пользователь (реакция): {reactor.user_id}")
    except RPCError as e:
        print(f"Не удалось получить реакции: {e}")

    return user_ids

def load_existing_users(file_path):
    """
    Загружает существующих пользователей из файла JSON.
    Если файл не найден, возвращается пустое множество.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return set(data.get("users", []))
    except FileNotFoundError:
        return set()

async def main():
    """
    Основной процесс:
    - Сканирует сообщения в канале/группе.
    - Получает пользователей, оставивших реакции и комментарии.
    - Сохраняет уникальных пользователей в JSON-файл.
    """
    await app.start()  # Запуск клиента
    all_user_ids = set()

    # Проверка типа чата (группа или канал)
    chat_info = await app.get_chat(channel_username)
    is_group = chat_info.type in ["group", "supergroup"]

    # Обработка сообщений
    async for message in app.get_chat_history(channel_username, limit=limit):
        # Если это группа, получаем пользователей, оставивших реакции
        if is_group:
            reaction_user_ids = await get_reactions(app, channel_username, message.id)
            all_user_ids.update(reaction_user_ids)

        # Получаем пользователей, оставивших комментарии
        try:
            async for comment in app.get_discussion_replies(channel_username, message.id):
                if comment.from_user:  # Игнорируем удалённые или анонимные комментарии
                    all_user_ids.add(comment.from_user.id)
                    print(f"Добавлен пользователь (комментарий): {comment.from_user.id}")
                await asyncio.sleep(delay)  # Задержка для снижения нагрузки
        except MsgIdInvalid:
            print(f"Пропуск сообщения с ID {message.id}: не поддерживает обсуждения.")
        except FloodWait as e:
            print(f"Превышен лимит запросов. Ожидание {e.value} секунд.")
            await asyncio.sleep(e.value)

    # Загружаем существующих пользователей из файла
    existing_users = load_existing_users(user_file)

    # Объединяем существующих пользователей с новыми
    all_user_ids.update(existing_users)

    # Сохраняем уникальные ID пользователей в JSON
    with open(user_file, 'w', encoding='utf-8') as f:
        json.dump({"users": list(all_user_ids)}, f, ensure_ascii=False, indent=4)

    print("\nДанные успешно обновлены и сохранены в 'users.json'")
    await app.stop()  # Завершение сессии клиента

# Запуск основного процесса
if __name__ == "__main__":
    app.run(main())

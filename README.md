# Telegram User Scraper

Этот скрипт позволяет собирать ID пользователей, которые оставили реакции или комментарии в Telegram канале/группе, и сохранять их в файл JSON.

## Настройка

1. Получите `api_id` и `api_hash` на [my.telegram.org](https://my.telegram.org).
2. Укажите:
   - `api_id` и `api_hash` в коде.
   - `channel_username` (имя канала или группы).
3. Установите зависимости:
   ```bash
   pip install pyrogram

# Database-Manager
## Запуск

Скопируйте `.env.example` в `.env` и отредактируйте `.env` файл, заполнив в нём все переменные окружения:

```bash
cp db_manager/.env.example db_manager/.env
```

Для управления зависимостями используется [poetry](https://python-poetry.org/),
требуется Python 3.10 и выше.

Установка зависимостей и запуск:

```bash
poetry install
poetry run python -m db_manager
```

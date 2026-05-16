# Production Commands

Этот файл для быстрого использования проекта без `dev`-режима.

## Что установить

### 1. Docker Desktop

Нужен для запуска всего проекта одной командой.

После установки проверьте:

```bash
docker --version
docker compose version
```

### 2. TablePlus

Нужен для визуальной проверки PostgreSQL.

## Основные команды

Запуск проекта:

```bash
cp .env.example .env
npm run prod:up
```

Остановить проект:

```bash
npm run prod:down
```

Посмотреть логи:

```bash
npm run prod:logs
```

Полностью сбросить базу данных:

```bash
npm run prod:reset-db
```

## Что открывать в браузере

- приложение: [http://localhost:5002](http://localhost:5002)
- API health: [http://localhost:5003/api/health](http://localhost:5003/api/health)
- search-service health: [http://localhost:8002/health](http://localhost:8002/health)

## Как визуально проверить Docker

Откройте Docker Desktop.

Должны быть контейнеры:

- `realestate-postgres-1`
- `realestate-search-service-1`
- `realestate-api-1`
- `realestate-web-1`

Их статус должен быть `Running`.

## Как визуально проверить PostgreSQL через TablePlus

Создайте новое подключение `PostgreSQL` со значениями:

- Host: `127.0.0.1`
- Port: `5432`
- User: `estateflow`
- Password: `estateflow_password`
- Database: `estateflow`

После подключения должны быть таблицы:

- `users`
- `clients`
- `client_search_profiles`
- `properties`
- `client_found_properties`
- `shortlist_items`
- `share_messages`
- `search_runs`

## Как проверить, что БД реально постоянная

1. Запустите проект:

```bash
npm run prod:up
```

2. Создайте клиента в приложении.
3. Запустите поиск.
4. Добавьте объект в подборку.
5. Откройте TablePlus и проверьте записи в:
   - `clients`
   - `properties`
   - `client_found_properties`
   - `shortlist_items`
6. Остановите проект:

```bash
npm run prod:down
```

7. Запустите снова:

```bash
npm run prod:up
```

8. Если записи остались, значит PostgreSQL persistent работает правильно.

## Какие команды вам не нужны для диплома

Можно игнорировать:

- `npm run dev`
- `npm run dev:split`
- `npm run dev:search`
- `npm run start:prod`

Для дипломного сценария вам достаточно только:

- `npm run prod:up`
- `npm run prod:down`
- `npm run prod:logs`
- `npm run prod:reset-db`

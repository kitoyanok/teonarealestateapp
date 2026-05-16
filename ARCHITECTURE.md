# EstateFlow Architecture

## Назначение системы

EstateFlow - это CRM для риелтора. Система хранит клиентов, их параметры поиска, запускает live-поиск недвижимости, сохраняет найденные объекты, формирует shortlist и подготавливает текст подборки для ручной отправки клиенту.

## Стек

- Frontend: React + Vite
- Backend API: Node.js + Express
- Search service: Python + FastAPI
- Парсинг: `httpx`, `BeautifulSoup4`, `lxml`
- База данных: PostgreSQL
- Деплой: Docker Compose + Nginx

Технически код frontend и backend написан на TypeScript, но в объяснении архитектуры для проекта стек остается простым и линейным: интерфейс на React, API на Express, парсинг на FastAPI, хранение данных в PostgreSQL.

## Frontend

Frontend расположен в `apps/web`.

Основные части:

- `src/main.tsx` - точка входа
- `src/app/App.tsx` - роутинг и инициализация приложения
- `src/shared/api.ts` - запросы к API
- `src/widgets/AppShell.tsx` - основной каркас интерфейса
- `src/pages/*` - страницы login, dashboard, clients, client, analytics, profile, help, settings

Как работает frontend:

1. При открытии приложения проверяется текущая сессия через `GET /api/auth/me`.
2. Если сессии нет, пользователь остается на экране логина.
3. После логина интерфейс запрашивает dashboard, клиентов, карточки клиентов и shortlist через API.
4. Все данные показываются в SPA без перезагрузки страницы.

## Backend API

Backend расположен в `apps/api`.

Основные части:

- `src/server.ts` - запуск HTTP-сервера
- `src/app.ts` - конфигурация Express
- `src/config.ts` - env-переменные
- `src/db/pool.ts` - подключение к PostgreSQL через `pg`
- `src/repositories/sql.ts` - SQL-запросы к базе
- `src/routes/auth.ts` - логин, logout, текущий пользователь
- `src/routes/dashboard.ts` - summary, activity, блок внимания
- `src/routes/clients.ts` - CRUD клиента, поиск, shortlist, share-message, mark-sent
- `src/routes/properties.ts` - детали объекта
- `src/services/searchService.ts` - orchestration поиска
- `src/services/messageService.ts` - генерация текста подборки

Как работает backend:

1. При логине API проверяет пользователя в PostgreSQL.
2. После авторизации API выдает JWT cookie `estateflow_token`.
3. Все защищенные маршруты проходят через `requireAuth`.
4. CRUD клиента работает напрямую с PostgreSQL через `pg` и SQL-запросы.
5. Поиск запускается через Node API, а фактический live-scraping выполняет Python service.

## Search service

Search service расположен в `apps/search-service`.

Основные части:

- `app/main.py` - FastAPI entrypoint
- `app/services/search.py` - основной pipeline
- `app/services/matcher.py` - матчинги под профиль клиента
- `app/adapters/*` - адаптеры внешних источников
- `app/schemas/*` - входные и выходные схемы

Как работает search service:

1. Node API передает параметры клиента в `POST /search`.
2. FastAPI вызывает адаптеры источников недвижимости.
3. HTML обрабатывается через `BeautifulSoup(..., "lxml")`.
4. Из ответа вырезаются мусорный текст, навигация, favicon, logo, icon, svg и маленькие картинки.
5. Возвращаются только нормализованные карточки объектов.
6. Если один источник не ответил, остальные продолжают работать.

## PostgreSQL

PostgreSQL - единственный источник данных. In-memory store и Prisma из рабочего контура убраны.

Схема инициализации лежит в `database/init.sql`.

Основные таблицы:

- `users`
- `clients`
- `client_search_profiles`
- `properties`
- `client_found_properties`
- `shortlist_items`
- `share_messages`
- `search_runs`

Что хранится в базе:

- пользователи
- клиенты и их контакты
- параметры поиска
- найденные объекты
- shortlist по клиенту
- тексты подборок
- история запусков поиска

## Поток данных

1. Риелтор создает клиента во frontend.
2. React отправляет запрос в Node API.
3. Node API сохраняет клиента и профиль поиска в PostgreSQL.
4. Node API вызывает Python search-service.
5. Python service ищет объекты на внешних сайтах и возвращает очищенный результат.
6. Node API сохраняет найденные объекты и связи с клиентом в PostgreSQL.
7. Во frontend риелтор добавляет объекты в shortlist.
8. Node API формирует текст подборки, который риелтор копирует и отправляет вручную.

## Локальный запуск

1. Установить зависимости `npm install`.
2. Поднять PostgreSQL.
3. Создать БД `estateflow`.
4. Выполнить `database/init.sql`.
5. Запустить `npm run dev`.

Порты:

- web: `5002`
- api: `5003`
- search-service: `8002`
- postgres: `5432`

## Docker и production

В production используется `docker-compose.yml`.

Контейнеры:

- `postgres`
- `search-service`
- `api`
- `web` на базе `nginx`

Nginx отдает собранный frontend и проксирует `/api/*` в Node API.

## Что важно для защиты проекта

Архитектуру можно объяснять так:

1. React отвечает за интерфейс.
2. Node.js принимает запросы, авторизует пользователя и работает с PostgreSQL.
3. Python отвечает за live-поиск и парсинг объектов недвижимости.
4. PostgreSQL хранит клиентов, параметры поиска, найденные объекты и подборки.
5. Docker Compose и Nginx используются для развертывания всех частей системы на сервере.

# EstateFlow / Тэона — упрощение стека, PostgreSQL, Docker и деплой

Файл для Codex и разработчика. Его нужно положить в корень проекта как `stack_deploy_plan.md`.

## 1. Цель документа

Нужно привести проект к понятному дипломному стеку, убрать лишние абстракции, сохранить уже работающий функционал поиска недвижимости и подготовить проект к нормальному запуску локально, через Docker и на хостинге с доменом.

Главная цель: **не переписывать продукт с нуля**, а аккуратно упростить архитектуру и сделать ее объяснимой для диплома.

---

## 2. Финальный стек проекта

Использовать следующий стек:

```text
Frontend:
React + JavaScript

Сборка frontend:
Vite

Backend API:
Node.js + Express

Search service:
Python + FastAPI

Парсинг:
httpx + BeautifulSoup4 + lxml

Database:
PostgreSQL

Deploy:
Docker Compose + Nginx

Production process:
контейнеры Docker
```

### Как объяснять стек на защите

```text
React отвечает за интерфейс.
Node.js принимает запросы от интерфейса, работает с базой данных и авторизацией.
Python отвечает за live-поиск и парсинг сайтов недвижимости.
PostgreSQL хранит клиентов, параметры поиска, найденные объекты и подборки.
Docker используется для деплоя всех частей приложения на сервер.
```

---

## 3. Что убрать из текущей архитектуры

Если в проекте есть эти зависимости или подходы, убрать или больше не использовать:

```text
Prisma
in-memory store
USE_MEMORY_STORE
сложные ORM
TanStack Query, если можно заменить обычными fetch-запросами
Zod, если валидация уже делается вручную
сложную многослойную архитектуру ради архитектуры
автоматическую отправку сообщений
канал отправки
```

### Почему убираем Prisma

Для диплома лучше показать понятную работу с PostgreSQL через SQL-запросы.

Вместо:

```text
Node.js → Prisma → PostgreSQL
```

Сделать:

```text
Node.js → pg → PostgreSQL
```

Рекомендуемая библиотека для Node.js:

```bash
npm install pg
```

---

## 4. Что оставить

Сохранить:

```text
React-интерфейс
страницы входа, главная, клиенты, карточка клиента, аналитика, профиль, помощь
поиск объектов по параметрам клиента
Python live-search service
PostgreSQL как основную базу
копирование телефона клиента
копирование текста подборки
модальное окно просмотра объявления
модальное окно подготовки подборки
```

---

## 5. Python: библиотека для парсинга

Использовать на Python:

```text
FastAPI — HTTP API для search-service
httpx — HTTP-запросы к сайтам
BeautifulSoup4 — разбор HTML
lxml — быстрый HTML/XML parser для BeautifulSoup
Pydantic — схемы входных и выходных данных
```

Установить:

```bash
pip install fastapi uvicorn httpx beautifulsoup4 lxml pydantic
```

Пример импорта:

```python
import httpx
from bs4 import BeautifulSoup

html = response.text
soup = BeautifulSoup(html, "lxml")
```

### Правила парсинга

1. Не использовать демо-объявления.
2. Не использовать логотипы, favicon и иконки сайта как фото объекта.
3. Если фото объекта не найдено — возвращать `image_url = null`.
4. На frontend показывать локальную заглушку “Фото не найдено”.
5. Название объекта должно быть нормализовано.
6. Описание должно быть очищено от мусора навигации, меню, SEO-текста и повторяющихся слов.
7. Сохранять ссылку на источник.
8. Не ломать поиск, если один источник не ответил.
9. По каждому источнику логировать количество найденных объектов и ошибки.

### Что считать валидным фото объекта

Можно использовать как фото:

```text
изображение квартиры
изображение дома
изображение ЖК
рендер здания
планировка, если другого фото нет
```

Нельзя использовать как фото:

```text
favicon
логотип застройщика
иконку сайта
иконки соцсетей
captcha
placeholder самого сайта
очень маленькие изображения
```

Минимальная проверка:

```text
ширина/высота изображения, если доступны, не меньше 250px
url не содержит favicon, logo, icon, sprite, svg
расширение jpg/jpeg/png/webp
```

---

## 6. PostgreSQL вместо memory-store и Prisma

Сделать PostgreSQL единственным источником данных.

### Убрать

```text
memoryStore
USE_MEMORY_STORE
локальные массивы вместо БД
Prisma client
schema.prisma
prisma migrations
```

### Добавить

```text
database/init.sql
apps/api/src/db/pool.js
apps/api/src/repositories/*.js
```

### Подключение к PostgreSQL

Файл:

```text
apps/api/src/db/pool.js
```

Пример:

```js
const pg = require("pg");

const pool = new pg.Pool({
  connectionString: process.env.DATABASE_URL,
});

module.exports = { pool };
```

---

## 7. Минимальная схема PostgreSQL

Создать файл:

```text
database/init.sql
```

Содержимое можно адаптировать под текущие поля проекта.

```sql
CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TABLE IF NOT EXISTS users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  login VARCHAR(100) UNIQUE NOT NULL,
  password_hash TEXT NOT NULL,
  name VARCHAR(150) NOT NULL DEFAULT 'Риелтор',
  phone VARCHAR(30),
  email VARCHAR(150),
  created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS clients (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  full_name VARCHAR(150) NOT NULL,
  phone VARCHAR(30) NOT NULL,
  property_type VARCHAR(20) NOT NULL CHECK (property_type IN ('apartment', 'house')),
  status VARCHAR(40) NOT NULL DEFAULT 'new',
  comment TEXT,
  created_at TIMESTAMP NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS client_search_profiles (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  client_id UUID REFERENCES clients(id) ON DELETE CASCADE,

  budget_min INTEGER,
  budget_max INTEGER,

  rooms TEXT[],
  area_min NUMERIC,
  area_max NUMERIC,

  house_area_min NUMERIC,
  house_area_max NUMERIC,
  land_area_min NUMERIC,
  land_area_max NUMERIC,

  locations TEXT[],
  districts TEXT[],
  completion_year VARCHAR(20),
  finishing VARCHAR(50),
  communications TEXT[],
  house_type VARCHAR(50),

  created_at TIMESTAMP NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS properties (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  external_id TEXT,
  source_name VARCHAR(150) NOT NULL,
  source_url TEXT NOT NULL,

  property_type VARCHAR(20) NOT NULL CHECK (property_type IN ('apartment', 'house')),
  title TEXT NOT NULL,
  description TEXT,
  price INTEGER,
  price_per_meter INTEGER,

  area NUMERIC,
  rooms VARCHAR(20),
  floor VARCHAR(50),
  completion_year VARCHAR(20),
  address TEXT,
  district VARCHAR(150),
  developer VARCHAR(150),
  complex_name VARCHAR(150),

  house_area NUMERIC,
  land_area NUMERIC,
  communications TEXT[],

  image_url TEXT,
  created_at TIMESTAMP NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS client_found_properties (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  client_id UUID REFERENCES clients(id) ON DELETE CASCADE,
  property_id UUID REFERENCES properties(id) ON DELETE CASCADE,
  match_percent INTEGER NOT NULL DEFAULT 0,
  match_reasons TEXT[],
  created_at TIMESTAMP NOT NULL DEFAULT NOW(),
  UNIQUE(client_id, property_id)
);

CREATE TABLE IF NOT EXISTS shortlist_items (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  client_id UUID REFERENCES clients(id) ON DELETE CASCADE,
  property_id UUID REFERENCES properties(id) ON DELETE CASCADE,
  created_at TIMESTAMP NOT NULL DEFAULT NOW(),
  UNIQUE(client_id, property_id)
);

CREATE TABLE IF NOT EXISTS share_messages (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  client_id UUID REFERENCES clients(id) ON DELETE CASCADE,
  message_text TEXT NOT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS search_runs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  client_id UUID REFERENCES clients(id) ON DELETE CASCADE,
  status VARCHAR(40) NOT NULL DEFAULT 'started',
  found_count INTEGER NOT NULL DEFAULT 0,
  error_text TEXT,
  created_at TIMESTAMP NOT NULL DEFAULT NOW(),
  finished_at TIMESTAMP
);
```

---

## 8. Переменные окружения

Создать `.env.example`:

```env
NODE_ENV=development

WEB_PORT=5002
API_PORT=5003
SEARCH_PORT=8002

DATABASE_URL=postgres://estateflow:estateflow_password@localhost:5432/estateflow

JWT_SECRET=change_me_for_production
SEARCH_SERVICE_URL=http://localhost:8002

DEMO_LOGIN=test
DEMO_PASSWORD=test
```

Для production:

```env
NODE_ENV=production

API_PORT=5003
SEARCH_PORT=8002

DATABASE_URL=postgres://estateflow:STRONG_PASSWORD@postgres:5432/estateflow

JWT_SECRET=VERY_LONG_RANDOM_SECRET
SEARCH_SERVICE_URL=http://search-service:8002
```

---

## 9. Локальный запуск без Docker на Mac

У пользователя локально Docker может быть не установлен. Поэтому нужно оставить обычный локальный запуск.

### Что нужно установить локально

```text
Node.js LTS
Python 3.11+
PostgreSQL
Git
```

### PostgreSQL на Mac

Самый простой вариант — Postgres.app.

#### Установка через Postgres.app

1. Скачать Postgres.app.
2. Перетащить приложение в `Applications`.
3. Открыть Postgres.app.
4. Нажать `Initialize`, если потребуется.
5. Убедиться, что PostgreSQL запущен.
6. Добавить `psql` в `PATH`, если нужно.

Проверка:

```bash
psql --version
```

Создать базу и пользователя:

```bash
createuser estateflow
createdb estateflow -O estateflow
psql -d estateflow
```

Внутри `psql` задать пароль:

```sql
ALTER USER estateflow WITH PASSWORD 'estateflow_password';
```

Проверить подключение:

```bash
psql "postgres://estateflow:estateflow_password@localhost:5432/estateflow"
```

Применить схему:

```bash
psql "postgres://estateflow:estateflow_password@localhost:5432/estateflow" -f database/init.sql
```

### Альтернатива через Homebrew

Если установлен Homebrew:

```bash
brew install postgresql
brew services start postgresql
```

Дальше так же создать пользователя и базу.

---

## 10. Docker на Mac

Docker нужен для деплоя и для удобного production-like запуска.

### Как скачать Docker Desktop

1. Открыть официальный сайт Docker.
2. Выбрать Docker Desktop for Mac.
3. Если Mac на M1/M2/M3/M4 — выбрать Apple Silicon.
4. Если Intel Mac — выбрать Intel Chip.
5. Скачать `.dmg`.
6. Перетащить Docker в `Applications`.
7. Запустить Docker Desktop.
8. Дождаться статуса `Docker is running`.

Проверка:

```bash
docker --version
docker compose version
```

Если Codex работает в среде без Docker, он должен подготовить Docker-файлы, но не обязан запускать контейнеры локально.

---

## 11. Docker Compose для проекта

Создать `docker-compose.yml` в корне.

Примерная структура сервисов:

```yaml
services:
  postgres:
    image: postgres:16
    container_name: estateflow_postgres
    restart: unless-stopped
    environment:
      POSTGRES_DB: estateflow
      POSTGRES_USER: estateflow
      POSTGRES_PASSWORD: estateflow_password
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./database/init.sql:/docker-entrypoint-initdb.d/init.sql
    ports:
      - "5432:5432"

  api:
    build:
      context: ./apps/api
    container_name: estateflow_api
    restart: unless-stopped
    environment:
      NODE_ENV: production
      API_PORT: 5003
      DATABASE_URL: postgres://estateflow:estateflow_password@postgres:5432/estateflow
      JWT_SECRET: change_me
      SEARCH_SERVICE_URL: http://search-service:8002
    depends_on:
      - postgres
      - search-service
    ports:
      - "5003:5003"

  search-service:
    build:
      context: ./apps/search-service
    container_name: estateflow_search
    restart: unless-stopped
    environment:
      SEARCH_PORT: 8002
    ports:
      - "8002:8002"

  web:
    build:
      context: ./apps/web
    container_name: estateflow_web
    restart: unless-stopped
    depends_on:
      - api
    ports:
      - "5002:80"

volumes:
  postgres_data:
```

---

## 12. Dockerfile для frontend

`apps/web/Dockerfile`:

```dockerfile
FROM node:20-alpine AS build

WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

FROM nginx:alpine

COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
```

`apps/web/nginx.conf`:

```nginx
server {
  listen 80;
  server_name _;

  root /usr/share/nginx/html;
  index index.html;

  location /api/ {
    proxy_pass http://api:5003/api/;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
  }

  location / {
    try_files $uri /index.html;
  }
}
```

---

## 13. Dockerfile для Node API

`apps/api/Dockerfile`:

```dockerfile
FROM node:20-alpine

WORKDIR /app

COPY package*.json ./
RUN npm install --omit=dev

COPY . .

EXPOSE 5003

CMD ["node", "src/server.js"]
```

Если проект пока TypeScript, либо перевести на JavaScript, либо добавить build:

```dockerfile
RUN npm run build
CMD ["node", "dist/server.js"]
```

Но предпочтительно упростить до JavaScript.

---

## 14. Dockerfile для Python search-service

`apps/search-service/Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8002

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8002"]
```

`apps/search-service/requirements.txt`:

```txt
fastapi
uvicorn
httpx
beautifulsoup4
lxml
pydantic
```

---

## 15. Какие данные дать Codex

Перед началом задачи дать Codex:

```text
1. Корень проекта.
2. Файл redesign.md.
3. Файл fixes_for_codex.md.
4. Этот файл stack_deploy_plan.md.
5. Папку views со скринами, logo.png и photo_1.
6. Текущий ARCHITECTURE.md.
7. Доступ к package.json всех частей проекта.
8. Желаемые порты:
   frontend 5002
   api 5003
   search-service 8002
   postgres 5432
9. Локальные данные PostgreSQL:
   DB name: estateflow
   DB user: estateflow
   DB password: estateflow_password
   DB host: localhost
   DB port: 5432
10. Production-домен, когда он появится.
```

---

## 16. Задача для Codex

Codex должен выполнить:

```text
1. Проанализировать текущую структуру проекта.
2. Убрать Prisma и memory-store.
3. Перевести работу с БД на PostgreSQL через pg.
4. Создать database/init.sql.
5. Создать или поправить .env.example.
6. Проверить все API-маршруты.
7. Сохранить текущий live-поиск через Python.
8. Убедиться, что найденные объекты сохраняются в PostgreSQL.
9. Сделать Dockerfile для web, api, search-service.
10. Сделать docker-compose.yml.
11. Добавить README с локальным запуском и Docker-запуском.
12. Сохранить UI и правки из redesign/fixes файлов.
13. Проверить, что приложение открывается на http://localhost:5002.
```

---

## 17. Команды для Codex

Codex должен использовать свои команды и инструменты:

```text
$ npm install
$ npm run dev
$ npm run build
$ npm run lint
$ node apps/api/src/server.js
$ python -m uvicorn app.main:app --reload --port 8002
$ psql ...
$ docker compose up --build
```

Если в среде Codex доступны плагины/скиллы, использовать их:

```text
@codebase
@terminal
@filesystem
@browser
@postgres
@docker
```

Если конкретный plugin недоступен, использовать ближайший аналог.

---

## 18. Что нужно для хостинга

Для production нужен VPS/VDS.

Рекомендуемый вариант:

```text
провайдер: Timeweb Cloud или аналогичный российский VPS
ОС: Ubuntu 22.04 или 24.04 LTS
CPU: от 2 vCPU
RAM: минимум 2 GB, лучше 4 GB
Disk: от 30 GB SSD/NVMe
Docker: установлен на сервере
Nginx: как reverse proxy
PostgreSQL: либо в Docker, либо отдельная managed database
Домен: .ru
SSL: Let's Encrypt
```

Для диплома достаточно:

```text
1 VPS
1 домен .ru
Docker Compose
Nginx
SSL
```

---

## 19. Что купить/создать в Timeweb

На Timeweb или похожем российском хостинге нужно:

```text
1. Зарегистрировать домен .ru.
2. Создать VPS/VDS на Ubuntu.
3. Получить IP-адрес сервера.
4. Настроить DNS A-запись:
   @ → IP сервера
   www → IP сервера
5. Подключиться по SSH.
6. Установить Docker и Docker Compose.
7. Склонировать проект с GitHub.
8. Настроить .env.production.
9. Запустить docker compose.
10. Настроить Nginx и SSL.
```

---

## 20. Пример домена

Можно выбрать домен в зоне `.ru`, например:

```text
teona-crm.ru
teona-estate.ru
teona-realty.ru
estateflow23.ru
```

Лучше короткое русскоязычное название:

```text
teona.ru
```

если свободен.

---

## 21. DNS

После покупки домена нужно создать записи:

```text
A     @      SERVER_IP
A     www    SERVER_IP
```

Если используется поддомен:

```text
A     app    SERVER_IP
```

Тогда приложение будет:

```text
https://app.domain.ru
```

---

## 22. Nginx reverse proxy на сервере

Можно использовать Nginx на сервере, который проксирует запросы в Docker.

Пример:

```nginx
server {
  listen 80;
  server_name example.ru www.example.ru;

  location / {
    proxy_pass http://127.0.0.1:5002;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
  }
}
```

После SSL будет HTTPS-конфиг.

---

## 23. SSL через Certbot

На Ubuntu:

```bash
sudo apt update
sudo apt install nginx certbot python3-certbot-nginx -y
sudo certbot --nginx -d example.ru -d www.example.ru
```

Проверка автообновления:

```bash
sudo certbot renew --dry-run
```

---

## 24. Команды на сервере

```bash
sudo apt update
sudo apt install git nginx -y

# Docker установить по официальной инструкции Docker для Ubuntu

git clone https://github.com/USER/estateflow.git
cd estateflow

cp .env.example .env.production
nano .env.production

docker compose --env-file .env.production up -d --build
docker compose ps
docker compose logs -f
```

---

## 25. Production env

Пример `.env.production`:

```env
NODE_ENV=production

DATABASE_URL=postgres://estateflow:STRONG_PASSWORD@postgres:5432/estateflow

JWT_SECRET=GENERATE_LONG_RANDOM_SECRET

API_PORT=5003
SEARCH_PORT=8002
SEARCH_SERVICE_URL=http://search-service:8002

DEMO_LOGIN=test
DEMO_PASSWORD=test
```

Важно:

```text
В production заменить пароль БД и JWT_SECRET.
Не коммитить .env.production в Git.
```

---

## 26. Что должно быть в README

README должен содержать:

```text
1. Что такое проект.
2. Стек.
3. Требования.
4. Локальный запуск без Docker.
5. Локальный запуск с Docker.
6. Переменные окружения.
7. Структура проекта.
8. Как запустить PostgreSQL.
9. Как применить database/init.sql.
10. Как открыть приложение.
11. Демо-доступ.
12. Как деплоить на сервер.
```

---

## 27. Локальный запуск без Docker

```bash
# 1. Установить зависимости frontend
cd apps/web
npm install

# 2. Установить зависимости api
cd ../api
npm install

# 3. Установить зависимости search-service
cd ../search-service
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 4. Создать PostgreSQL базу
createdb estateflow

# 5. Применить схему
psql "postgres://estateflow:estateflow_password@localhost:5432/estateflow" -f ../../database/init.sql

# 6. Запустить сервисы
```

Лучше сделать root scripts:

```json
{
  "scripts": {
    "dev": "concurrently \"npm --prefix apps/api run dev\" \"npm --prefix apps/web run dev\" \"npm --prefix apps/search-service run dev\""
  }
}
```

---

## 28. Definition of Done

Работа считается выполненной, если:

```text
1. Проект запускается локально на http://localhost:5002.
2. PostgreSQL используется как единственная база.
3. Prisma удален или не используется.
4. In-memory store удален или не используется.
5. Клиент создается и сохраняется в PostgreSQL.
6. Параметры клиента сохраняются в PostgreSQL.
7. Поиск запускается через Python service.
8. Найденные объекты сохраняются в PostgreSQL.
9. Подборка сохраняется в PostgreSQL.
10. Текст подборки генерируется из реальных shortlist items.
11. Телефон копируется отдельно.
12. Docker Compose поднимает web, api, search-service и postgres.
13. README содержит инструкции запуска.
14. UI не сломан после изменения стека.
15. Порты:
    web 5002
    api 5003
    search 8002
    postgres 5432
```

---

## 29. Важные запреты

```text
Не добавлять Go.
Не добавлять Prisma обратно.
Не использовать in-memory store.
Не добавлять автоматическую отправку сообщений.
Не добавлять канал отправки.
Не использовать логотипы сайтов как фото объектов.
Не показывать демо-объекты вместо live-результатов.
Не ломать текущий пользовательский флоу.
```

---

## 30. Итоговая архитектура

```text
Browser
  ↓
React frontend
  ↓ /api
Node.js Express API
  ↓
PostgreSQL

Node.js Express API
  ↓ /search
Python FastAPI search-service
  ↓
Публичные сайты недвижимости
```

Приложение должно оставаться простым:

```text
Frontend показывает интерфейс.
Backend хранит данные и управляет клиентами.
Python ищет недвижимость.
PostgreSQL хранит все состояние.
Docker упрощает деплой.
```

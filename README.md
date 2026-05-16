# EstateFlow

EstateFlow - CRM для риелтора с live-поиском недвижимости, подборками и подготовкой текста для ручной отправки клиенту.

## Финальный стек

- Frontend: React + Vite
- Backend API: Node.js + Express
- Search service: Python + FastAPI
- Парсинг: `httpx` + `BeautifulSoup4` + `lxml`
- Database: PostgreSQL
- Deploy: Docker Compose + Nginx

Исходники frontend и backend сейчас написаны на TypeScript, но архитектурно стек остается простым: React на клиенте, Express на API, FastAPI для парсинга, PostgreSQL как единственная база данных.

## Что работает

- логин
- dashboard
- список клиентов
- карточка клиента
- live-поиск объектов
- shortlist
- копирование телефона
- копирование текста подборки
- модальное окно просмотра объекта
- профиль, помощь, аналитика, настройки

## Локальный запуск

1. Установить зависимости:

```bash
npm install
```

2. Поднять PostgreSQL и создать БД `estateflow`.

3. Скопировать переменные:

```bash
cp .env.example .env
```

4. Применить SQL-схему:

```bash
psql postgres://estateflow:estateflow_password@localhost:5432/estateflow -f database/init.sql
```

5. Запустить приложение:

```bash
npm run dev
```

Открывать:

- frontend: [http://localhost:5002](http://localhost:5002)
- api health: [http://localhost:5003/api/health](http://localhost:5003/api/health)
- search-service docs: [http://localhost:8002/docs](http://localhost:8002/docs)

Демо-доступ:

```text
test / test
```

## Docker Compose

```bash
cp .env.example .env
docker compose up --build
```

После запуска:

- приложение: [http://localhost:5002](http://localhost:5002)
- API внутри Docker: `http://api:5003`
- search-service внутри Docker: `http://search-service:8002`
- PostgreSQL внутри Docker: `postgres://estateflow:estateflow_password@postgres:5432/estateflow`

## Переменные окружения

```env
WEB_PORT=5002
API_PORT=5003
PYTHON_SEARCH_PORT=8002
POSTGRES_PORT=5432
JWT_SECRET=change-me-in-production
SEARCH_SERVICE_URL=http://localhost:8002
NODE_ENV=development
DATABASE_URL=postgres://estateflow:estateflow_password@localhost:5432/estateflow
DEMO_LOGIN=test
DEMO_PASSWORD=test
```

## Структура

```text
apps/
  web/              React/Vite frontend
  api/              Express API + pg
  search-service/   FastAPI live search
database/
  init.sql          PostgreSQL schema
deploy/
  nginx.conf        production reverse proxy
docker-compose.yml
ARCHITECTURE.md
```

## Как устроен поток

1. Риелтор входит в систему.
2. Создает клиента и параметры поиска.
3. Node API сохраняет клиента в PostgreSQL.
4. Node API вызывает Python search-service.
5. Python собирает live-объекты с источников и возвращает очищенные данные.
6. Node API сохраняет найденные объекты, shortlist и историю поиска в PostgreSQL.
7. Во frontend риелтор выбирает объекты и копирует готовый текст подборки клиенту.

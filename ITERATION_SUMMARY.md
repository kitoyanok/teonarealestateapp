# Iteration Summary

## Current Version

- Git version: `v0.1.4`
- Branch: `main`

## Current Stack State

- Frontend: React + Vite
- Backend API: Node.js + Express
- Search service: Python + FastAPI
- Database: PostgreSQL via `pg`
- Deploy: Docker Compose + Nginx

## Already Simplified

- Prisma removed from runtime and source flow
- `memoryStore` removed from source flow
- PostgreSQL schema moved to `database/init.sql`
- API works through SQL repository layer and `pg`
- Dockerfiles and `docker-compose.yml` added
- Nginx config added for production frontend serving

## Still Not Fully Simplified

The project is not yet reduced to the absolute minimum requested in every area.

Still present on the frontend:

- TypeScript
- `@tanstack/react-query`
- `react-hook-form`
- `zod`

These do not block deployment, PostgreSQL, or hosting, but if the goal is a stricter diploma stack, they should be removed in a separate cleanup iteration.

## Immediate Next Goal

Finalize persistent PostgreSQL flow through Docker Compose, then prepare production deployment to Timeweb and domain binding from REG.RU.

## Current PostgreSQL Status

- PostgreSQL runs in Docker Compose
- API uses `pg` and `DATABASE_URL`
- search results are written to:
  - `properties`
  - `client_found_properties`
  - `search_runs`
- shortlist is written to:
  - `shortlist_items`
- data persistence is provided by Docker named volume:
  - `estateflow-postgres`
- compose healthchecks now gate service startup order for:
  - `postgres`
  - `search-service`
  - `api`

## Production-Only Usage

- Added root quick-start file: `PROD_COMMANDS.md`
- Added production aliases:
  - `npm run prod:up`
  - `npm run prod:down`
  - `npm run prod:logs`
  - `npm run prod:reset-db`
- For diploma usage, `dev` commands can now be ignored

## What Was Done In This Iteration

- property titles are now normalized more aggressively in search-service
- bad titles like `Все новостройки`, `Избранное`, `Отзывы` are filtered
- property descriptions are generated from structured characteristics instead of page garbage
- bad images are filtered more strictly
- listing cards no longer show photos
- property list cards no longer show match percent or progress bars
- client page no longer contains the large activity chart
- dashboard KPI cards are calmer and no longer show fake trend percentages
- parsing documentation added:
  - `docs/PARSING_SOURCES.md`
- search QA checklist added:
  - `docs/SEARCH_QA_CHECKLIST.md`
- unit tests added for matcher and normalization:
  - `apps/search-service/tests/test_matcher.py`
  - `apps/search-service/tests/test_normalization.py`
- diploma note draft started:
  - `docs/Пояснительная_записка_Тэона.md`
  - `Пояснительная_записка_Тэона.docx`

## How Parsing Works Right Now

- sources are not discovered automatically
- sources are hardcoded in `apps/search-service/app/adapters/sources.py`
- one base adapter normalizes output to a common schema
- apartments and houses use different source lists
- if one source fails, search continues with other sources
- logo/icon/favicon URLs are filtered out before images are saved
- object title is rebuilt from rooms/area/location when the source title is garbage

## Connected Sources

Apartment sources currently include:

- НАШ.ДОМ.РФ
- Домострой Краснодар
- ССК
- ВКБ-Новостройки
- ГК ТОЧНО
- DOGMA
- СК Семья
- Неометрия
- НВМ
- ЕкатеринодарИнвест-Строй
- Novostroyka123
- Novostrojki-KRD
- 23kvartiri
- Krasdom

House sources currently include:

- Doma-kr
- КП Краснодар
- Поселки Краснодара
- 23kvartiri
- Novostrojki-KRD

## How Search Was Checked

- TypeScript typecheck: passed
- production build: passed
- Python unit tests for matcher and normalization: passed
- live external search was not re-run from this Codex environment because outbound network is limited
- a manual QA checklist for local verification is prepared in `docs/SEARCH_QA_CHECKLIST.md`

## Remaining Work

- run manual local search QA against real websites on your machine
- visually inspect updated frontend in browser after local startup
- improve and expand diploma explanatory note based on your reference sample
- optionally simplify frontend stack further if you want to remove extra libraries before final defense

## DOCX Note

- `Пояснительная_записка_Тэона.docx` is generated
- visual render QA through the documents renderer could not be completed in this environment because `soffice` is unavailable

## What Will Be Needed From User

For PostgreSQL and deploy:

- Timeweb server access method: SSH or panel
- server IP
- SSH user
- SSH password or SSH private key
- target OS on server
- preferred app domain/subdomain

For domain setup:

- bought domain at REG.RU
- access to DNS zone or exact DNS records to set

For production env:

- production `JWT_SECRET`
- final domain names for frontend and API

## Notes

- This file should be updated after each implementation iteration.
- Each iteration should end with a new git commit and push when GitHub access works.

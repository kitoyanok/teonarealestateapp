# Iteration Summary

## Current Version

- Pending git version for this iteration: `v0.1.8`
- Branch: `main`

## Main Goal Of This Iteration

Довести пояснительную записку до полноценного дипломного объема и структуры по образцу [67_Погосян_ПЗ.docx](/Users/like-shockpritotskaya-event/Documents/Зубач/Codex/realestate/67_Погосян_ПЗ.docx), а не оставлять ее как короткий черновик.

## What Was Done

- сильно расширена итоговая ПЗ:
  - [67_Зубач_ПЗ.docx](/Users/like-shockpritotskaya-event/Documents/Зубач/Codex/realestate/67_Зубач_ПЗ.docx)
- переработан генератор:
  - [scripts/build_zubach_pz.py](/Users/like-shockpritotskaya-event/Documents/Зубач/Codex/realestate/scripts/build_zubach_pz.py)
- в ПЗ добавлены:
  - анализ предметной области
  - функциональные и нефункциональные требования
  - расширенные таблицы прецедентов
  - сценарии успешного выполнения и исключения
  - описание архитектуры
  - описание физической модели данных
  - описание frontend, backend, search-service
  - подробное описание алгоритмов парсинга и расчета match score
  - описание сохранения результатов поиска и shortlist в PostgreSQL
  - описание production-развертывания через Docker Compose
- добавлены новые визуальные материалы:
  - wireframes
  - диаграмма вариантов использования
  - блок-схема подбора
  - схема архитектуры
  - схема БД
  - mock-скриншоты экранов приложения
  - mock-скриншот просмотра таблицы БД
- добавлены большие приложения:
  - полный SQL-скрипт БД
  - листинги backend-модулей
  - листинги search-service
  - листинги ключевых frontend-страниц
  - эксплуатационные markdown-документы проекта

## PZ Structure Now

В [67_Зубач_ПЗ.docx](/Users/like-shockpritotskaya-event/Documents/Зубач/Codex/realestate/67_Зубач_ПЗ.docx) сейчас есть:

- титульный лист
- содержание
- введение
- `1 Назначение и цели разработки`
- `1.1 Анализ предметной области`
- `1.2 Требования к разрабатываемой системе`
- `2 Разработка технического проекта`
- `2.1 Определение спецификаций программного обеспечения`
- `2.2 Проектирование модели данных`
- `2.3 Проектирование интерфейса пользователя`
- `3 Рабочий проект`
- `3.1 Обоснование выбора средств разработки`
- `3.2 Разработка физической модели данных`
- `3.3 Программная реализация модулей`
- `3.3.1 Реализация frontend-модуля`
- `3.3.2 Реализация backend API`
- `3.3.3 Реализация search-service и алгоритмов парсинга`
- `3.3.4 Алгоритм сохранения результатов поиска в PostgreSQL`
- `3.3.5 Формирование подборки и текста сообщения`
- `3.4 Тестирование программных модулей`
- `3.5 Разработка эксплуатационной документации`
- `3.6 Развертывание через Docker Compose`
- заключение
- список источников
- приложения А, Б, В, Г, Д, Е, Ж, И, К, Л, М, Н, П, Р

## Formatting Rules Applied

По замечаниям преподавателя в документе закреплен единый стиль оформления шагов:

- не используется формат `1. текст шага`
- используется формат `Действие №1. Текст действия.`
- в конце действия ставится точка
- тот же принцип использован в сценариях и тест-кейсах

## Visual Assets Added

Файлы лежат в:

- [docs/assets/zubach_pz](/Users/like-shockpritotskaya-event/Documents/Зубач/Codex/realestate/docs/assets/zubach_pz)

Добавлены:

- `01_use_case.png`
- `02_activity.png`
- `03_architecture.png`
- `04_er_schema.png`
- `05_wireframe_login.png`
- `06_wireframe_dashboard.png`
- `07_wireframe_clients.png`
- `08_wireframe_client_card.png`
- `09_screen_login.png`
- `10_screen_dashboard.png`
- `11_screen_clients.png`
- `12_screen_client_card.png`
- `13_screen_message_modal.png`
- `14_screen_db_view.png`

## Volume Check

- текстовый объем DOCX после расширения: около `14 000` слов
- это уже не короткий черновик, а полноценный расширенный дипломный документ

## Project State

- Frontend: React + Vite
- Backend API: Node.js + Express
- Search service: Python + FastAPI
- Database: PostgreSQL via `pg`
- Deploy: Docker Compose + Nginx

## PostgreSQL And Search State

- API сохраняет клиентов в PostgreSQL
- результаты поиска сохраняются в:
  - `properties`
  - `client_found_properties`
  - `search_runs`
- подборки сохраняются в:
  - `shortlist_items`
- тексты сообщений сохраняются в:
  - `share_messages`
- parser описан в ПЗ на основе реальной логики из:
  - [apps/search-service/app/adapters/base.py](/Users/like-shockpritotskaya-event/Documents/Зубач/Codex/realestate/apps/search-service/app/adapters/base.py)
  - [apps/search-service/app/services/search.py](/Users/like-shockpritotskaya-event/Documents/Зубач/Codex/realestate/apps/search-service/app/services/search.py)
  - [apps/search-service/app/services/matcher.py](/Users/like-shockpritotskaya-event/Documents/Зубач/Codex/realestate/apps/search-service/app/services/matcher.py)

## Verification

- генератор [scripts/build_zubach_pz.py](/Users/like-shockpritotskaya-event/Documents/Зубач/Codex/realestate/scripts/build_zubach_pz.py) выполняется успешно
- новый [67_Зубач_ПЗ.docx](/Users/like-shockpritotskaya-event/Documents/Зубач/Codex/realestate/67_Зубач_ПЗ.docx) собирается без ошибок
- новые PNG-материалы сгенерированы
- структура документа расширена и включает дополнительные приложения

## Render QA Status

- автоматическая render-проверка `docx -> png` через documents renderer по-прежнему недоступна в этой среде
- причина: отсутствует `soffice`
- это ограничение окружения, а не ошибка сборки DOCX

## Commands

- пересобрать ПЗ:
  - `/Users/like-shockpritotskaya-event/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 scripts/build_zubach_pz.py`

## Remaining Work

- открыть [67_Зубач_ПЗ.docx](/Users/like-shockpritotskaya-event/Documents/Зубач/Codex/realestate/67_Зубач_ПЗ.docx) в Word
- обновить содержание
- проверить титульный лист: группа, руководитель, кафедральные данные
- после замечаний преподавателя внести уже точечные правки по формулировкам и составу приложений

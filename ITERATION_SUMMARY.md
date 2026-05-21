# Iteration Summary

## Current Version

- Pending git version for this iteration: `v0.1.7`
- Branch: `main`

## What Was Done In This Iteration

- полностью переделана пояснительная записка под тему проекта `Тэона` по структуре образца [67_Погосян_ПЗ.docx](/Users/like-shockpritotskaya-event/Documents/Зубач/Codex/realestate/67_Погосян_ПЗ.docx)
- создан новый итоговый Word-файл:
  - [67_Зубач_ПЗ.docx](/Users/like-shockpritotskaya-event/Documents/Зубач/Codex/realestate/67_Зубач_ПЗ.docx)
- добавлен новый генератор ПЗ:
  - [scripts/build_zubach_pz.py](/Users/like-shockpritotskaya-event/Documents/Зубач/Codex/realestate/scripts/build_zubach_pz.py)
- сгенерированы визуальные артефакты для отчета:
  - диаграмма вариантов использования
  - блок-схема сценария подбора
  - архитектурная схема
  - схема БД PostgreSQL
  - wireframes основных окон
- все артефакты лежат в:
  - [docs/assets/zubach_pz](/Users/like-shockpritotskaya-event/Documents/Зубач/Codex/realestate/docs/assets/zubach_pz)

## What Is In The New PZ

Документ [67_Зубач_ПЗ.docx](/Users/like-shockpritotskaya-event/Documents/Зубач/Codex/realestate/67_Зубач_ПЗ.docx) теперь содержит:

- титульный лист
- содержание
- введение
- раздел `1 Назначение и цели разработки`
- раздел `2 Разработка технического проекта`
  - спецификация ПО
  - таблицы прецедентов
  - сценарии успешного выполнения
  - сценарии исключений
  - блок-схема
  - схема архитектуры
  - схема БД
  - wireframes интерфейса
- раздел `3 Рабочий проект`
  - обоснование выбора стека
  - физическая модель данных
  - программная реализация модулей
  - тестирование
  - эксплуатационная документация
- заключение
- список источников
- приложения А-Ж

## Formatting Rules Applied

По замечанию преподавателя оформление шагов приведено к одному виду:

- в сценариях используется формат `Действие №1. ...`
- в тест-кейсах шаги тоже записаны как `Действие №1. ...`
- обычная нумерация вида `1. ...` для шагов не используется
- в конце действий ставится точка, а не `;`

## Diagrams And Wireframes Added

- `01_use_case.png` — диаграмма вариантов использования
- `02_activity.png` — блок-схема подбора объектов
- `03_architecture.png` — архитектурная схема системы
- `04_er_schema.png` — схема БД PostgreSQL
- `05_wireframe_login.png` — окно авторизации
- `06_wireframe_dashboard.png` — главная страница
- `07_wireframe_clients.png` — список клиентов
- `08_wireframe_client_card.png` — карточка клиента

## Project State

- Frontend: React + Vite
- Backend API: Node.js + Express
- Search service: Python + FastAPI
- Database: PostgreSQL via `pg`
- Deploy: Docker Compose + Nginx

## Persistent PostgreSQL State

- PostgreSQL работает через Docker Compose
- API подключается через `pg`
- результаты поиска сохраняются в:
  - `properties`
  - `client_found_properties`
  - `search_runs`
- подборки сохраняются в:
  - `shortlist_items`
- сообщения сохраняются в:
  - `share_messages`
- данные переживают перезапуск контейнеров за счет volume `estateflow-postgres`

## Verification

- генератор [scripts/build_zubach_pz.py](/Users/like-shockpritotskaya-event/Documents/Зубач/Codex/realestate/scripts/build_zubach_pz.py) выполняется успешно
- итоговый файл [67_Зубач_ПЗ.docx](/Users/like-shockpritotskaya-event/Documents/Зубач/Codex/realestate/67_Зубач_ПЗ.docx) собран
- визуальные PNG-артефакты сгенерированы

## Render QA Status

- попытка прогнать `docx -> png` через render tool была выполнена
- полная render-проверка не завершилась, потому что в среде отсутствует `soffice`
- это ограничение окружения, а не ошибка генератора DOCX

## Commands

- пересобрать ПЗ:
  - `/Users/like-shockpritotskaya-event/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 scripts/build_zubach_pz.py`

## Remaining Work

- вручную открыть [67_Зубач_ПЗ.docx](/Users/like-shockpritotskaya-event/Documents/Зубач/Codex/realestate/67_Зубач_ПЗ.docx) в Word и обновить содержание
- после просмотра преподавателем внести точечные правки по формулировкам, если они появятся
- при следующей итерации можно добавить еще более детализированные SQL-приложения и расширенные тест-кейсы, если это потребуется

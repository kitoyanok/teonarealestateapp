# Iteration Summary

## Current Version

- Git version for this iteration: `v0.1.9`
- Branch: `main`

## What Was Fixed In This Iteration

Исправлены проблемы из клиентской карточки и главной страницы:

- блок `В подборке / Найдено` на странице клиента разделен на две отдельные плашки
- названия объектов приведены к короткому формату:
  - квартира: количество комнат + площадь
  - дом: площадь дома
- кнопки в карточках объектов прижаты к нижнему краю карточки
- описания объектов очищаются гораздо жестче
- устранен дефект с ложной комнатностью вида `21`
- KPI на главной переведены на реальные временные ряды без фальшивых процентов
- в KPI и графиках проценты больше не рисуются как декоративный шум: показываются только реальные данные

## Files Changed

- [apps/web/src/pages/ClientPage.tsx](/Users/like-shockpritotskaya-event/Documents/Зубач/Codex/realestate/apps/web/src/pages/ClientPage.tsx)
- [apps/web/src/shared/format.ts](/Users/like-shockpritotskaya-event/Documents/Зубач/Codex/realestate/apps/web/src/shared/format.ts)
- [apps/web/src/pages/DashboardPage.tsx](/Users/like-shockpritotskaya-event/Documents/Зубач/Codex/realestate/apps/web/src/pages/DashboardPage.tsx)
- [apps/web/src/entities/types.ts](/Users/like-shockpritotskaya-event/Documents/Зубач/Codex/realestate/apps/web/src/entities/types.ts)
- [apps/web/src/styles/global.css](/Users/like-shockpritotskaya-event/Documents/Зубач/Codex/realestate/apps/web/src/styles/global.css)
- [apps/api/src/routes/dashboard.ts](/Users/like-shockpritotskaya-event/Documents/Зубач/Codex/realestate/apps/api/src/routes/dashboard.ts)
- [apps/api/src/repositories/sql.ts](/Users/like-shockpritotskaya-event/Documents/Зубач/Codex/realestate/apps/api/src/repositories/sql.ts)
- [apps/search-service/app/adapters/base.py](/Users/like-shockpritotskaya-event/Documents/Зубач/Codex/realestate/apps/search-service/app/adapters/base.py)
- [apps/search-service/app/utils/text.py](/Users/like-shockpritotskaya-event/Documents/Зубач/Codex/realestate/apps/search-service/app/utils/text.py)
- [apps/search-service/tests/test_normalization.py](/Users/like-shockpritotskaya-event/Documents/Зубач/Codex/realestate/apps/search-service/tests/test_normalization.py)

## Client Page Changes

### Summary tiles

Раньше счетчики `В подборке` и `Найдено` были объединены в один горизонтальный блок.

Теперь:

- каждый счетчик вынесен в отдельную плашку
- блок выглядит как две отдельные карточки
- это упрощает чтение и соответствует замечанию по UI

### Property card titles

Раньше заголовки тянули в себя:

- названия ЖК
- адреса
- мусор из контактов
- фрагменты маркетинговых блоков

Теперь заголовки принудительно сокращены:

- `1-к квартира, 40.6 м²`
- `2-к квартира, 53.8 м²`
- `Дом 128 м²`

Фронтенд тоже делает fallback в этот формат, поэтому даже старые грязные записи в БД не должны больше показывать длинные мусорные названия.

### Property card layout

Раньше кнопки могли зависеть от высоты контента и визуально ехать вверх.

Теперь:

- карточка растягивается по высоте
- body карточки сделан через flex column
- блок кнопок уходит вниз через `margin-top: auto`

### Property descriptions

Раньше в модалке и карточках мог показываться мусорный текст:

- SEO-обрывки
- контакты
- набор цен и счетчиков
- служебные слова

Теперь:

- search-service пытается использовать очищенное текстовое описание с сайта
- описания с телефонами, `контакты`, `в продаже`, маркетинговыми блоками и цифровым шумом отбрасываются
- если нормального описания нет, frontend собирает чистый fallback из:
  - типа объекта
  - площади
  - района
  - цены
  - источника

## Room Parsing Fix

Проблема `21 комната` возникала из-за слишком грубого regex для комнатности.

Что изменено:

- parser теперь ищет только реальные паттерны комнатности:
  - `1-к`
  - `2-комн`
  - `3-комнатная`
- значения больше `8` считаются невалидными и отбрасываются
- frontend дополнительно страхует уже сохраненные данные и не показывает неадекватное число комнат в drawer и карточках

## Dashboard Changes

### KPI cards

Раньше mini-bars были почти декоративными и не отражали отдельные реальные метрики.

Теперь каждая карточка использует собственный реальный временной ряд за 7 дней:

- `Клиенты в работе` -> количество созданных клиентов по дням
- `Найдено объектов` -> сумма `search_runs.total_found`
- `В подборках` -> число `shortlist_items` по дням
- `Готово к отправке` -> количество `share_messages.sent_marked_at` по дням

### Percentages

Фальшивые проценты больше не используются.

Если данных нет:

- график в KPI-карточке просто не рисуется

### Main chart

Главный график активности на dashboard теперь тоже завязан на реальные данные из БД:

- линия показывает найденные объекты
- светлые бары показывают добавления в подборки
- tooltip показывает реальные значения

## Search Normalization Changes

В search-service усилена очистка описаний:

- отбрасываются телефоны
- отбрасываются `контакты`, `подобрать`, `заказать звонок`, `в продаже`
- вырезается часть цифрового мусора и повторяющихся ценовых фраз
- сохраняются только достаточно длинные и внятные фразы

Также заголовки в backend теперь тоже собираются в коротком формате без ЖК и адреса.

## Tests And Verification

Проверки этой итерации:

- `npm run typecheck` — пройдено
- `npm run build` — пройдено
- `cd apps/search-service && .venv/bin/python -m unittest discover -s tests -v` — пройдено

Добавлены/обновлены тесты:

- плохой title квартиры нормализуется в короткий формат
- дом нормализуется в формат `Дом N м²`
- фраза `21 квартира` не считается комнатностью
- описание с телефоном и словом `Контакты` отбрасывается

## Important Note

Для новых корректных описаний и названий лучше повторно запустить поиск по клиенту:

- старые записи в PostgreSQL уже могли сохраниться с прошлой грязной нормализацией
- frontend теперь их сильно маскирует и чистит
- но полный эффект будет после нового search run и обновления записей в БД

## Remaining Work

- при необходимости вручную проверить клиентскую карточку в браузере после повторного поиска
- если захотите, следующей итерацией можно отдельно довести карточки объектов до еще более строгого одинакового визуального шаблона

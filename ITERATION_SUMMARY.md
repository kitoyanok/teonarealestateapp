# Iteration Summary

## Current Version

- Git version: `v0.1.19`
- Branch: `main`

## What Was Changed

- вместо старой одиночной учетной записи введен список преднастроенных риелторов;
- в backend добавлен seed нескольких учетных записей сотрудников;
- экран входа переведен на рабочие логины;
- `.env.example` очищен от старых временных переменных для одиночного входа;
- `README.md` переписан в коротком и полезном формате;
- содержимое `full_readme.md` перенесено в `README.md`, после чего `full_readme.md` удален;
- из корня проекта удалены лишние промежуточные markdown-файлы с правками и служебными заметками;
- создан файл `Диплом_структура_ПЗ.md` с планом ПЗ по официальному заданию и по референсу;
- текстовые файлы очищены от лишних служебных формулировок, где это было уместно.

## Key Files

- `README.md`
- `ITERATION_SUMMARY.md`
- `Диплом_структура_ПЗ.md`
- `apps/api/src/data/realtors.ts`
- `apps/api/src/repositories/db.ts`
- `apps/api/src/repositories/sql.ts`
- `apps/api/src/server.ts`
- `apps/web/src/pages/LoginPage.tsx`
- `.env.example`

## Realtor Accounts

- `ivan.nikitin`
- `kirill.nabiev`
- `ilya.berezin`
- `marina.nikiforova`
- `nikita.zubach`

Общий пароль:

`Teona2026!`

## What Still Needs Attention

- пройтись по всем поддерживаемым исходникам и добавить в них понятные поясняющие комментарии;
- при необходимости обновить ПЗ и скриншоты так, чтобы логины на изображениях тоже соответствовали новым учетным записям;
- при желании отдельно обновить `Пояснительная_записка_Тэона.docx`, если она еще используется как промежуточный черновик.

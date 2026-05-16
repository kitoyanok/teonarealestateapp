# Iteration Summary

## Current Version

- Git version: `v0.1.1`
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

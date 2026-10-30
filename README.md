Modern News Aggregator (Django 5.2 • Scrapy 2.13.3 • Celery 5.5.3 • Redis 6.4.0 • React 19 • React Router 7)
Frontend - React 19, React Router 7, Vite, TypeScript, Tailwind CSS, React Query (TanStack Query) for data fetching, Zod for schema validation - State: minimal global state (auth tokens + user)
Backend - Django 5.2, djangorestframework, drf‑spectacular (OpenAPI), django‑filters, psycopg[binary], django‑cors‑headers - Auth: djangorestframework‑simplejwt (access+refresh)
Search: PostgreSQL FTS (tsvector) + trigram (pg_trgm).
Dev stack: Dockerized dev/prod setup with docker-compose.yml + docker-compose.dev.yml 

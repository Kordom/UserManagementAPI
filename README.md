# User Management API

FastAPI + PostgreSQL + SQLAlchemy user management API with HTTP Basic authentication.

## Features
- Register users (`POST /users`)
- Self profile:
  - `GET /users/me`
  - `PUT /users/me` (password change)
- Admin management:
  - `GET /users` (list)
  - `GET /users/{user_id}` (details)
  - `PATCH /users/{user_id}/activate`
  - `PATCH /users/{user_id}/deactivate`
  - `DELETE /users/{user_id}`
- Rules:
  - The first registered user must automatically become an admin; all others are regular
users.
  - Regular users can view and update only their own data.
  - Deactivated users must not be able to access protected routes.
  - Admins cannot activate, deactivate, or delete their own account.
  - Administrators can view and manage all users.


## Tech stack
- FastAPI
- PostgreSQL
- SQLAlchemy ORM
- Alembic migrations
- pytest (integration tests)

---

## Run with Docker

### 1) Configure environment
Create `.env` from example:

```bash
cp .env.example .env
```

### 2) Start Services
```
docker compose up -d --build
```
API docs:

Swagger UI: http://localhost:8000/docs
### 3) Run Migrations
```
docker compose exec api alembic upgrade head
```
## Usage for Users

### To Check Health
```
curl -X 'GET' \
  'http://localhost:8000/health' \
  -H 'accept: application/json'
```
### To register user
```
curl -X 'POST' \
  'http://localhost:8000/users' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "username": "admin",
  "password": "admin123"
}'
```

### To check who am i
```
curl -X 'GET' \
  'http://localhost:8000/users/me' \
  -H 'accept: application/json'
```

### To update password 
```
curl -X 'PUT' \
  'http://localhost:8000/users/me' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "password": "admin123456789"
}'
```

## Usage for Admins
### To list all users
```
curl -X 'GET' \
  'http://localhost:8000/users' \
  -H 'accept: application/json'
```

### To get user by id
```
curl -X 'GET' \
  'http://localhost:8000/users/1' \
  -H 'accept: application/js
```

### To Delete user
```
curl -X 'DELETE' \
  'http://localhost:8000/users/3' \
  -H 'accept: */*'
```

### To Activate/Deactivate
```
curl -X 'PATCH' \
  'http://localhost:8000/users/2/activate' \
  -H 'accept: application/json'
```
### OR 
```
curl -X 'PATCH' \
  'http://localhost:8000/users/3/deactivate' \
  -H 'accept: application/json'
```

## To run Tests inside Docker
### First TestDb have to be created, otherwise it will drop data from productionDB
```
docker compose exec db psql -U app -d postgres -c "CREATE DATABASE app_test;"    
```
### Then Run
```
docker compose exec -e DATABASE_URL=postgresql+psycopg2://app:app@db:5432/app_test api pytest -q      
```

## Notes
### If you change DB credentials in .env, PostgreSQL may keep old credentials due to persisted volume. To reset local DB data:
```
docker compose down -v
docker compose up -d
docker compose exec api alembic upgrade head
```
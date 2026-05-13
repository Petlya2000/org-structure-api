# Organizational Structure API

API для управления иерархической структурой подразделений и сотрудников.

## 📋 Содержание

- [Технологии](#технологии)
- [Требования](#требования)
- [Быстрый запуск](#быстрый-запуск)
- [API Endpoints](#api-endpoints)
- [Примеры запросов](#примеры-запросов)
- [Бизнес-логика](#бизнес-логика-и-ограничения)
- [Тестирование](#запуск-тестов)
- [Миграции](#миграции-базы-данных)
- [Структура проекта](#структура-проекта)

## 🚀 Технологии

- **FastAPI** - веб-фреймворк
- **PostgreSQL** - база данных
- **SQLAlchemy** - ORM
- **Alembic** - миграции
- **Docker** - контейнеризация
- **Pytest** - тестирование

## 📦 Требования

- Docker Desktop
- Docker Compose

## 🔧 Быстрый запуск

```bash
# Клонировать репозиторий
git clone https://github.com/Petlya2000/org-structure-api.git
cd org-structure-api

# Запустить проект
docker-compose up --build

После запуска API будет доступно:

API: http://localhost:8000

Документация Swagger: http://localhost:8000/docs
```
```bash
📡 API Endpoints
Метод	Эндпоинт	Описание
POST	/departments/	Создать подразделение
POST	/departments/{id}/employees/	Создать сотрудника
GET	/departments/{id}	Получить подразделение с деревом
PATCH	/departments/{id}	Обновить/переместить подразделение
DELETE	/departments/{id}	Удалить подразделение
Параметры
GET /departments/{id}

depth - глубина вложенных подразделений (1-5, по умолчанию 1)

include_employees - включить сотрудников в ответ (true/false)

DELETE /departments/{id}

mode - режим удаления (cascade или reassign)

reassign_to_department_id - ID подразделения для переназначения (обязателен при mode=reassign)
```
```bash

📝 Примеры запросов
Создание подразделения
bash
curl -X POST http://localhost:8000/departments/ \
  -H "Content-Type: application/json" \
  -d '{"name":"IT Department","parent_id":null}'
Ответ:

json
{
  "id": 1,
  "name": "IT Department",
  "parent_id": null,
  "created_at": "2026-05-13T19:55:32.431241"
}
Создание сотрудника
bash
curl -X POST http://localhost:8000/departments/1/employees/ \
  -H "Content-Type: application/json" \
  -d '{"full_name":"Иван Петров","position":"Senior Developer","hired_at":"2024-01-15"}'
Получение дерева подразделений
bash
curl "http://localhost:8000/departments/1?depth=2&include_employees=true"
Перемещение подразделения
bash
curl -X PATCH http://localhost:8000/departments/2 \
  -H "Content-Type: application/json" \
  -d '{"parent_id":1}'
Удаление подразделения
bash
# Каскадное удаление
curl -X DELETE "http://localhost:8000/departments/2?mode=cascade"

# Удаление с переназначением сотрудников
curl -X DELETE "http://localhost:8000/departments/2?mode=reassign&reassign_to_department_id=1"
```
```bash

🧠 Бизнес-логика и ограничения
✅ Название подразделения: длина 1-200 символов, уникально в пределах одного родителя

✅ Полное имя сотрудника: длина 1-200 символов

✅ Должность: длина 1-200 символов

✅ Нельзя создать подразделение-родитель самого себя

✅ Нельзя создать цикл в дереве (возвращается 409 Conflict)

✅ При удалении в режиме cascade удаляется всё поддерево

✅ При удалении в режиме reassign сотрудники переназначаются в другое подразделение
```
```bash

🧪 Запуск тестов
bash
docker-compose exec app pytest -v
Результат:

text
================== 6 passed in 1.73s ==================
```
```bash

🗄️ Миграции базы данных
bash
# Создать миграцию
docker-compose exec app alembic revision --autogenerate -m "migration_name"

# Применить миграции
docker-compose exec app alembic upgrade head
```
```bash

📁 Структура проекта
text
app/
├── api/              # Роутеры API
│   └── routers/      # Эндпоинты
├── core/             # Конфигурация и БД
├── models/           # SQLAlchemy модели
├── schemas/          # Pydantic схемы
├── services/         # Бизнес-логика
├── utils/            # Вспомогательные функции
└── tests/            # Pytest тесты
```

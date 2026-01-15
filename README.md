# Deribit Price Tracker

Сервис для отслеживания цен криптовалют BTC и ETH с биржи Deribit. Собирает данные каждую минуту и предоставляет REST
API для доступа к ним.

## Функциональность

- **Автоматический сбор цен**: Каждую минуту получает index цены для BTC/USD и ETH/USD с Deribit API
- **Хранение в PostgreSQL**: Надежное сохранение данных с уникальными индексами
- **REST API**: Полнофункциональный API для получения исторических данных
- **Контейнеризация**: Полностью развертывается через Docker Compose
- **Обработка ошибок**: Graceful retry механизмы и логирование

## API Эндпоинты

### Получение всех цен по тикеру

```http
GET /prices?ticker=btc_usd
GET /prices?ticker=eth_usd
```

### Получение последней цены

```http
GET /prices/latest?ticker=btc_usd
GET /prices/latest?ticker=eth_usd
```

### Получение цен по диапазону дат

```http
GET /prices/by-date?ticker=btc_usd&from_ts=1700000000&to_ts=1700000600
```

## Развертывание (Docker)

### Требования

- Docker и Docker Compose
- Git

### Шаги для развертывания

1. **Клонирование репозитория**

```bash
git clone https://gitlab.com/ViktorShadr/deribit-price-tracker.git
cd deribit-price-tracker
```

2. **Настройка переменных окружения**

```bash
cp .env.example .env
# Отредактируйте .env при необходимости
```

3. **Запуск сервисов**

```bash
docker-compose up -d
```

В Docker Compose запускаются API, PostgreSQL, Redis, Celery worker и Celery beat
для периодического сбора данных.

4. **Проверка работоспособности**

```bash
# Проверка API
curl http://localhost:8000/health

# Проверка получения цен
curl "http://localhost:8000/prices/latest?ticker=btc_usd"
```

---

## Локальный запуск (API и Celery без Docker)

В данном режиме приложение (API и Celery) запускается локально,
а инфраструктурные сервисы (PostgreSQL и Redis) — в Docker.

### Требования

- Python 3.12
- Docker и Docker Compose (для PostgreSQL и Redis)

### Шаги

1. **Подготовка окружения**

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. **Настройка переменных окружения**

```bash
cp .env.example .env
# Отредактируйте .env при необходимости
```

3. **Запуск инфраструктуры (PostgreSQL и Redis)**

```bash
docker-compose up -d db redis
```

4. **Применение миграций**

```bash
alembic upgrade head
```

5. **Запуск API**

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

6. **Запуск Celery worker и beat (в отдельных терминалах)**

**Linux / macOS:**

```bash
celery -A worker.celery_app:celery_app worker --loglevel=info
```

**Windows:**

```bash
celery -A worker.celery_app:celery_app worker --loglevel=info --pool=solo
```

```bash
celery -A worker.celery_app:celery_app beat --loglevel=info
```

### Переменные окружения

| Переменная           | Значение по умолчанию          | Описание                        |
|----------------------|--------------------------------|---------------------------------|
| `POSTGRES_PASSWORD`  | change_me                      | Пароль PostgreSQL               |
| `DATABASE_URL`       | -                              | URL подключения к БД            |
| `CELERY_BROKER_URL`  | redis://localhost:6379/0       | Redis брокер для Celery         |
| `CELERY_BACKEND_URL` | redis://localhost:6379/1       | Redis backend для результатов   |
| `DERIBIT_BASE_URL`   | https://www.deribit.com/api/v2 | URL Deribit API                 |
| `TICKERS`            | btc_usd,eth_usd                | Список тикеров для отслеживания |

## Design Decisions

### 1. Выбор httpx вместо aiohttp

**Решение**: Использован синхронный httpx клиент вместо асинхронного aiohttp

**Обоснование**:

- Celery задачи выполняются в синхронном контексте
- httpx предоставляет современный API и лучшую производительность для синхронных запросов
- Упрощает код и отладку в контексте Celery worker
- httpx является преемником requests и рекомендуется для новых проектов

### 2. PostgreSQL с уникальными индексами

**Решение**: PostgreSQL с уникальным индексом (ticker, ts)

**Обоснование**:

- Гарантирует целостность данных на уровне БД
- Предотвращает дубликаты при одновременных запросах
- Поддерживает сложные запросы и агрегацию
- Индекс (ticker, ts) оптимизирует основные запросы API

### 3. Трехслойная архитектура (Clean Architecture)

**Решение**: API → Service → CRUD → Database

**Обоснование**:

- **Разделение ответственности**: Каждый слой имеет четкую зону ответственности
- **Тестируемость**: Легко мокать зависимости на каждом уровне
- **Масштабируемость**: Простое добавление новой бизнес-логики
- **Поддерживаемость**: Изменения в одном слое не затрагивают другие
- **Отсутствие глобальных переменных**: Все зависимости передаются через конструкторы

### 4. Валидация тикеров на нескольких уровнях

**Решение**: Валидация в Pydantic, SQLAlchemy Check Constraint

**Обоснование**:

- Pydantic обеспечивает валидацию на входе API
- Check Constraint в БД гарантирует целостность данных
- Enum в схемах предоставляет автодокументацию API
- Многоуровневая защита от некорректных данных

### 5. ООП подход с dataclass

**Решение**: Использование frozen dataclass для сервисов и клиентов

**Обоснование**:

- **Инкапсуляция**: Данные и методы объединены в одном объекте
- **Неизменяемость**: Frozen dataclass предотвращает случайные изменения
- **Чистый код**: Явное объявление зависимостей в конструкторе
- **Типизация**: Автоматическая генерация __init__ с типами

### 6. Контекстный менеджер для БД сессий

**Решение**: `get_db_context()` для Celery задач

**Обоснование**:

- Гарантирует правильное закрытие сессий
- Автоматический rollback при ошибках
- Избегает глобальных зависимостей
- Улучшает тестируемость кода

### 7. Graceful обработка ошибок в Celery

**Решение**: Автоматический retry с exponential backoff

**Обоснование**:

- Внешние API могут быть временно недоступны
- Exponential backoff снижает нагрузку на сервис
- Детальное логирование для мониторинга
- Изолирует ошибки от основного потока

### 8. Нейминг и структура проекта

**Решение**: Четкая структура с говорящими именами

**Обоснование**:

- **Самодокументируемый код**: Имена функций и переменных объясняют назначение
- **Единый стиль**: Следование PEP 8 и общепринятым конвенциям
- **Логическая группировка**: Связанный код находится в одном модуле
- **Предсказуемость**: Структура проекта соответствует лучшим практикам FastAPI

## Структура проекта

```
deribit-price-tracker/
├── app/
│   ├── api/           # FastAPI роуты
│   │   └── routes.py  # Основные эндпоинты API
│   ├── core/          # Конфигурация
│   │   └── config.py  # Настройки и переменные окружения
│   ├── db/            # Модели, CRUD, зависимости
│   │   ├── base.py    # SQLAlchemy Base
│   │   ├── crud.py    # CRUD операции
│   │   ├── deps.py    # Зависимости для БД
│   │   └── models.py  # SQLAlchemy модели
│   ├── schemas/       # Pydantic модели
│   │   └── price.py   # Схемы цен и валидация
│   ├── services/      # Бизнес-логика
│   │   ├── deribit_client.py  # Клиент Deribit API
│   │   └── prices_service.py  # Сервис работы с ценами
│   └── main.py        # FastAPI приложение
├── worker/            # Celery задачи
│   ├── celery_app.py  # Настройка Celery
│   └── tasks.py       # Задачи сбора данных
├── alembic/           # Миграции БД
│   └── versions/      # Версии миграций
├── tests/             # Unit тесты
│   └── test_api.py    # Тесты API эндпоинтов
├── docker-compose.yml # Оркестрация контейнеров
├── Dockerfile         # Сборка приложения
├── requirements.txt   # Зависимости Python
├── .env.example      # Пример переменных окружения
└── README.md         # Документация
```

## Технологический стек

- **Backend**: FastAPI, Python 3.12
- **База данных**: PostgreSQL 16
- **ORM**: SQLAlchemy 2.0
- **Миграции**: Alembic
- **Очередь задач**: Celery + Redis
- **HTTP клиент**: httpx
- **Контейнеризация**: Docker + Docker Compose
- **Тестирование**: pytest, httpx
- **Валидация**: Pydantic

## Тестирование

### Запуск тестов

```bash
# Запуск всех тестов
python -m pytest tests/

# Запуск с покрытием
python -m pytest tests/ --cov=app

# Запуск конкретного теста
python -m pytest tests/test_api.py::ApiTests::test_health_ok
```

### Примеры тестов

```python
# Тест получения последней цены
async def test_latest_returns_200_when_data_exists(self):
    r = await self.client.get("/prices/latest", params={"ticker": "btc_usd"})
    self.assertEqual(r.status_code, 200)


# Тест валидации обязательных параметров
async def test_prices_requires_ticker_returns_422(self):
    r = await self.client.get("/prices")
    self.assertEqual(r.status_code, 422)
```

## Мониторинг и логирование

### Логи

- Application logs: stdout контейнеров
- Celery worker logs: детальные логи задач
- Database logs: PostgreSQL логи

### Health checks

- API: `GET /health`
- Database: PostgreSQL health check
- Redis: Redis ping check

## Производительность

### Оптимизации

- Индексы БД для основных запросов
- Connection pooling для PostgreSQL
- Эффективная обработка дубликатов
- Batch операции в Celery задачах

### Метрики

- Время ответа API: < 50ms
- Частота сбора данных: 1 минута
- Размер хранилища: ~1MB/год на тикер

## Траблшутинг

### Частые проблемы

1. **API недоступен**

```bash
# Проверить статус контейнеров
docker-compose ps

# Проверить логи
docker-compose logs app
```

2. **Нет данных в БД**

```bash
# Проверить логи worker
docker-compose logs worker

# Проверить статус Celery задач
docker-compose exec worker celery -A worker.celery_app:get_celery_app inspect active
```

3. **Проблемы с БД**

```bash
# Пересоздать БД с миграциями
docker-compose down -v
docker-compose up -d
```

## Авторы

Viktor Shadrin - Backend Developer

## Версии

- v1.0.0 - Initial release с полным функционалом

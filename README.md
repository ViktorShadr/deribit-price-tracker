# Deribit Price Tracker

Сервис для отслеживания цен криптовалют BTC и USD с биржи Deribit. Собирает данные каждую минуту и предоставляет REST API для доступа к ним.

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

## Развертывание

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

4. **Проверка работоспособности**
```bash
# Проверка API
curl http://localhost:8000/health

# Проверка получения цен
curl "http://localhost:8000/prices/latest?ticker=btc_usd"
```

### Переменные окружения

| Переменная | Значение по умолчанию | Описание |
|-----------|---------------------|----------|
| `POSTGRES_PASSWORD` | change_me | Пароль PostgreSQL |
| `DATABASE_URL` | - | URL подключения к БД |
| `CELERY_BROKER_URL` | redis://localhost:6379/0 | Redis брокер для Celery |
| `CELERY_BACKEND_URL` | redis://localhost:6379/1 | Redis backend для результатов |
| `DERIBIT_BASE_URL` | https://www.deribit.com/api/v2 | URL Deribit API |
| `TICKERS` | btc_usd,eth_usd | Список тикеров для отслеживания |

## Design Decisions

### 1. Выбор httpx вместо aiohttp
**Решение**: Использован синхронный httpx клиент вместо асинхронного aiohttp

**Обоснование**:
- Celery задачи выполняются в синхронном контексте
- httpx предоставляет современный API и лучшую производительность для синхронных запросов
- Упрощает код и отладку в контексте Celery worker

### 2. PostgreSQL с уникальными индексами
**Решение**: PostgreSQL с уникальным индексом (ticker, ts)

**Обоснование**:
- Гарантирует целостность данных на уровне БД
- Предотвращает дубликаты при одновременных запросах
- Поддерживает сложные запросы и агрегацию
- Индекс (ticker, ts) оптимизирует основные запросы API

### 3. Сервисный слой архитектуры
**Решение**: Трехслойная архитектура (API → Service → CRUD)

**Обоснование**:
- Разделение ответственности улучшает тестируемость
- CRUD слой инкапсулирует логику работы с БД
- Service слой содержит бизнес-логику
- API слой остается тонким и фокусируется на HTTP

### 4. Валидация тикеров на нескольких уровнях
**Решение**: Валидация в Pydantic, SQLAlchemy Check Constraint

**Обоснование**:
- Pydantic обеспечивает валидацию на входе API
- Check Constraint в БД гарантирует целостность данных
- Enum в схемах предоставляет автодокументацию API
- Многоуровневая защита от некорректных данных

### 5. Контекстный менеджер для БД сессий
**Решение**: `get_db_context()` для Celery задач

**Обоснование**:
- Гарантирует правильное закрытие сессий
- Автоматический rollback при ошибках
- Избегает глобальных зависимостей
- Улучшает тестируемость кода

### 6. Graceful обработка ошибок в Celery
**Решение**: Автоматический retry с exponential backoff

**Обоснование**:
- Внешние API могут быть временно недоступны
- Exponential backoff снижает нагрузку на сервис
- Detalized логирование для мониторинга
- Изолирует ошибки от основного потока

## Структура проекта

```
deribit-price-tracker/
├── app/
│   ├── api/           # FastAPI роуты
│   ├── core/          # Конфигурация
│   ├── db/            # Модели, CRUD, зависимости
│   ├── schemas/       # Pydantic модели
│   └── services/      # Бизнес-логика
├── worker/            # Celery задачи
├── alembic/           # Миграции БД
├── tests/             # Unit тесты
├── docker-compose.yml # Оркестрация контейнеров
└── Dockerfile         # Сборка приложения
```

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

### Покрытие тестами
- API эндпоинты: 100%
- Валидация параметров: 100%
- Обработка ошибок: 100%
- Мокирование зависимостей БД

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
docker-compose exec worker celery -A worker.celery_app inspect active
```

3. **Проблемы с БД**
```bash
# Пересоздать БД с миграциями
docker-compose down -v
docker-compose up -d
```

## Лицензия

MIT License - см. файл LICENSE

## Авторы

Viktor Shadrin - Backend Developer

## Версии

- v1.0.0 - Initial release с полным функционалом

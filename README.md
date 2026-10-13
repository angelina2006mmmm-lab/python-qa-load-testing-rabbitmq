# Premium Notifications Lab — Python QA, RabbitMQ, Locust

## Дополнительный QA-проект: Business Community QA Lab

[Учебное тестирование сообщества предпринимателей — 20 REST API интеграционных тестов, web/mobile чек-листы, Postman, SQL и баг-репорт](extensions/business-community-qa-lab/README.md).

[Успешный запуск GitHub Actions](https://github.com/angelina2006mmmm-lab/python-qa-load-testing-rabbitmq/actions/runs/38375494828). Используются только синтетические данные и независимый API-мок, **не система СберБизнес**. Web/mobile сценарии представлены как непроведённые тесты.


Учебный pet-проект для портфолио QA Automation (Python). **Не связан с МТС и не использует реальные клиентские данные.** Демонстрирует тестирование REST API, работу с брокером RabbitMQ и запуск нагрузочных сценариев в Locust.

## Стек

Python 3.12, FastAPI, pytest, unittest.mock, RabbitMQ (pika), SQLite, Locust, Docker Compose, GitHub Actions.

## Схема

```text
Клиент / Locust
      |
      v
FastAPI: POST /jobs ---> SQLite: status=queued
      |
      v
RabbitMQ (durable queue)
      |
      v
Worker (consumer) ---> SQLite: status=done
      ^
      |
Клиент: GET /jobs/{id} (получить статус из SQLite)
```

Создаваемая через API задача — пример уведомления подписки. Это модель для упражнений, а не реальный сервис.

## Запуск в Ubuntu (WSL) с Docker

Нужен Docker Engine/ Docker Desktop с интеграцией WSL и Docker Compose v2. Проверьте `docker --version` и `docker compose version`.

```bash
docker compose up --build -d
```

- API: http://localhost:8000/docs
- RabbitMQ Management: http://localhost:15672 (логин `demo`, пароль `demo`, **только локально**)

Проверьте, что worker действительно обрабатывает сообщение:

```bash
python3 scripts/smoke.py
```

Ожидаемый смысл результата: строка `PASS: message delivered and consumed, status=done`. При проблемах проверьте `docker compose logs -f api worker rabbitmq`.

### Пример API-запросов

```bash
curl -s -X POST http://localhost:8000/jobs \
  -H 'Content-Type: application/json' \
  -d '{"message":"Premium trial notification"}'
```

Ответ с `id`, затем:

```bash
curl http://localhost:8000/jobs/<JOB_ID>
```

### Unit/API автотесты (RabbitMQ не нужен)

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-dev.txt
python -m pytest -q
```

Они используют временную SQLite-базу и подменяют реальную отправку в RabbitMQ через `monkeypatch`. Это позволяет повторять проверки на CI без Docker.

### Locust: нагрузочное тестирование

Запускаем Locust в отдельном Docker-контейнере:

```bash
docker compose --profile load up --build -d locust
```

Откройте http://localhost:8089. Для начала задайте **5 пользователей, скорость 1 пользователь/сек**. Посмотрите RPS, p95 времени отклика и количество ошибок. Затем увеличьте нагрузку до 10 пользователей. Это локальные ориентиры, а не обещание производительности.

Для запуска без веб-интерфейса и записи CSV в `reports/`:

```bash
docker compose --profile load run --rm locust -f /workspace/loadtest/locustfile.py --host http://api:8000 --headless -u 10 -r 2 -t 1m --csv /reports/local-test
```

**Не отправляйте нагрузку на чужие серверы без разрешения.** В примерах указан только локальный стенд.

### Завершение

```bash
docker compose --profile load down
```

Для полного удаления данных БД: `docker compose --profile load down -v`.

## Сценарии

См. [`docs/TEST_PLAN.md`](docs/TEST_PLAN.md). В проекте есть позитивные/негативные проверки API, тест обработки сообщений и тест недоступности брокера. Нагрузочные сценарии создают сообщения, читают их состояние и проверяют `/health`.

## Какие навыки демонстрирует проект

Проект демонстрирует разработку учебного API, producer/consumer через RabbitMQ, автоматизацию проверок pytest и сценарии Locust. После запуска можно изучить реальные RPS, p95 времени ответа и частоту ошибок. Конкретные показатели зависят от локального компьютера и нагрузки, поэтому здесь не приводятся.

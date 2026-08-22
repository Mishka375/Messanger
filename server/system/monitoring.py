from prometheus_client import Counter, Gauge, Histogram, generate_latest, CONTENT_TYPE_LATEST, start_http_server
import threading


users_total = Gauge (
    "users_total",
    "Users total in db"
)

users_online = Gauge (
    "users_online",
    "Users online",
)

messages_count = Counter (
    "messages_count",
    "Total message count"
)

redis_operations_count = Counter (
    "redis_operations_count",
    "Redis operations count"
)

redis_errors_count = Counter (
    "redis_errors_count",
    "Redis errors count"
)

sql_request_time = Histogram(
    "sql_request_time",
    "SQL time of request",
    buckets=(0.005, 0.01, 0.025, 0.05, 0.075, 0.1, 0.25, 0.5, 0.75, 1.0, 2.5, 5.0, 7.5, 10.0)
)

sql_request_count = Counter (
    "sql_request_count",
    "SQL count of request"
)

sql_request_errors = Counter (
    "sql_request_errors",
    "Count of SQL errors"
)

sql_request_queue = Gauge (
    "sql_request_queue",
    "SQL request queue"
)

start_http_server(8001)
print("Мониторинг запущен")


"""

Counter
Счетчик только +
.inc()       (+1)
.inc(n: int) (+n)

Gauge
Счетчик +-
.set(n: int) (=n)
.inc()       (+1)
.dec()       (-1)

Enum
Состояние (строка)
.state(s: str) (=s)

Info
Постоянные данные (Версия, ветка и т.п.)
.info({a:b, c:d})

Histogram
Гистрограмма (-==--, график среднего значения из введенных m)
.observe(m)

Summery
Сводка
.observe(m)

"""

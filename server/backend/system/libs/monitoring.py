from prometheus_client import Counter, Gauge, Histogram, generate_latest, CONTENT_TYPE_LATEST, start_http_server


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


redis_request_count = Counter (
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
    buckets=(0.005, 0.01, 0.05, 0.2, 0.5, 1.0, 5.0)
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


request_time = Histogram (
    "request_time",
    "Request time",
    buckets=(0.05, 0.1, 1.0, 3.0, 5.0, 7.0, 10.0)
)

request_count = Counter (
    "request_count",
    "Total request count"
)

request_errors = Counter (
    "request_errors",
    "Request errors"
)

request_queue = Gauge (
    "request_queue",
    "Request queue"
)


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
from prometheus_client import Counter, Histogram

QUERY_REQUESTS = Counter(
    "cortex_ai_query_requests_total", "Total /query requests", ["mode"]
)
QUERY_LATENCY = Histogram(
    "cortex_ai_query_latency_seconds", "Time spent answering a /query request"
)
INGESTION_REQUESTS = Counter(
    "cortex_ai_ingestion_requests_total", "Total ingestion attempts", ["status"]
)
INGESTION_LATENCY = Histogram(
    "cortex_ai_ingestion_latency_seconds", "Time spent ingesting a document"
)

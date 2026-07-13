from prometheus_fastapi_instrumentator import Instrumentator


def setup_prometheus(app):
    instrumentator = Instrumentator(
        should_group_status_codes=True,
        should_ignore_untemplated=True,
        should_instrument_requests_inprogress=True,
        excluded_handlers=[
            "/metrics",
            "/docs",
            "/openapi.json",
            "/redoc"
        ]
    )

    instrumentator.instrument(app).expose(
        app,
        endpoint="/metrics",
        include_in_schema=False
    )

def main() -> None:
    import uvicorn

    from dogjob.infra.config import get_settings

    settings = get_settings()
    uvicorn.run("dogjob.app:app", host=settings.host, port=settings.port)

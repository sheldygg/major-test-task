from contextlib import asynccontextmanager
from typing import Annotated, AsyncGenerator

import uvicorn
from fastapi import APIRouter, Depends, FastAPI
from faststream.rabbit import RabbitBroker
from faststream.rabbit.opentelemetry import RabbitTelemetryMiddleware

from exchange.common.config import load_config
from exchange.common.exchange import queue
from exchange.common.logging import configure_logging
from exchange.common.telemetry import setup_telemetry
from exchange.notification_service.models import SendMessage
from .depends_stub import Stub

router = APIRouter()


@router.get("/sendMessage")
async def hello_http(
    chat_id: int, text: str, broker: Annotated[RabbitBroker, Depends(Stub(RabbitBroker))], *, pin: bool = False
) -> dict:
    await broker.publish(
        SendMessage(chat_id=chat_id, text=text),
        queue=queue,
        priority=1,
    )

    return {"success": True, "chat_id": chat_id, "text": text, "pin": pin}


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    config = load_config()

    tracer_provider = setup_telemetry(
        service_name="web",
        otlp_endpoint=config.trace.otlp_endpoint,
    )

    telemetry_middleware = RabbitTelemetryMiddleware(tracer_provider=tracer_provider)
    broker = RabbitBroker(url=config.rabbit.url, middlewares=(telemetry_middleware,))
    await broker.connect()

    app.dependency_overrides[RabbitBroker] = lambda: broker
    yield
    await broker.close()


def main() -> FastAPI:
    configure_logging()
    app = FastAPI(lifespan=lifespan)
    app.include_router(router)
    return app


if __name__ == "__main__":
    uvicorn.run(main(), host="0.0.0.0", port=8080)

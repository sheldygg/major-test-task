import asyncio

from aiogram import Bot, Dispatcher
from faststream.rabbit import RabbitBroker
from faststream.rabbit.opentelemetry import RabbitTelemetryMiddleware

from exchange.common.config import load_config
from exchange.common.logging import configure_logging
from exchange.common.telemetry import setup_telemetry
from .handlers import router


async def main() -> None:
    configure_logging()
    config = load_config()
    tracer_provider = setup_telemetry(
        service_name="tg_bot",
        otlp_endpoint=config.trace.otlp_endpoint,
    )

    telemetry_middleware = RabbitTelemetryMiddleware(tracer_provider=tracer_provider)
    broker = RabbitBroker(url=config.rabbit.url, middlewares=(telemetry_middleware,))
    await broker.connect()

    bot = Bot(token=config.telegram.bot_token.get_secret_value())
    dispatcher = Dispatcher(broker=broker)
    dispatcher.include_router(router)

    await dispatcher.start_polling(bot)


asyncio.run(main())

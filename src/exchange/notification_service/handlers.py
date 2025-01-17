import asyncio
import logging

from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError, TelegramRetryAfter
from faststream import Context
from faststream.rabbit import RabbitBroker, RabbitMessage, RabbitRouter
from opentelemetry import trace

from exchange.common.exchange import exchange, queue
from .models import SendMessage

logger = logging.getLogger(__name__)
tracer = trace.get_tracer(__name__)
router = RabbitRouter()


@router.subscriber(queue, exchange)
async def notifications_handler(
    msg: RabbitMessage,
    message: SendMessage,
    bot: Bot = Context("bot"),
    broker: RabbitBroker = Context("broker"),
) -> None:
    logger.info("Received message [%s]", message)

    try:
        sent_message = await bot.send_message(
            chat_id=message.chat_id,
            text=message.text,
        )

        if message.pin:
            try:
                await sent_message.pin()
            except TelegramBadRequest:
                logger.exception("TelegramBadRequest while pining, message: %s", message)

        logger.info("Message sent: chat_id=%d, message_id=%d", message.chat_id, sent_message.message_id)
        await msg.ack()

    except TelegramBadRequest:
        logger.exception("TelegramBadRequest while sending, message: %s", message)
        await msg.ack()  # message with bad data(?), so we ack it

    except TelegramForbiddenError:
        logger.exception("TelegramForbiddenError while sending, message: %s", message)
        await msg.ack()  # user blocked bot, so we ack it

    except TelegramRetryAfter as ex:
        logger.exception(
            "TelegramRetryAfter while sending, retry_after=%d, message: %s",
            ex.retry_after,
            message,
        )
        await asyncio.sleep(ex.retry_after)
        await broker.publish(
            msg.body,
            queue="notifications",
            headers={"x-delay": 10000, "retry_count": msg.headers.get("retry_count", 0) + 1},
            exchange=exchange,
            priority=1,
        )

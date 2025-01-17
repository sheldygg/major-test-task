from aiogram import F, Router
from aiogram.filters import Command, CommandObject
from aiogram.types import Message
from faststream.rabbit import RabbitBroker

from exchange.common.exchange import queue
from exchange.notification_service.models import SendMessage

router = Router()
text = "Hi major!!\n\n" "<code>/send_message user_id text</code> - send message to user\n"


@router.message(Command("start"))
async def handle_start(message: Message) -> None:
    await message.reply(text)


@router.message(Command("send_message", magic=F.args))
async def handle_send_message(
    message: Message,
    broker: RabbitBroker,
    command: CommandObject,
) -> None:
    if not command.args:
        raise ValueError("Command args is empty")

    user_id, text = command.args.split(maxsplit=1)
    await broker.publish(
        SendMessage(chat_id=int(user_id), text=text),
        queue=queue,
        priority=1,
    )
    await message.reply("Message sent to queue")


@router.message(Command("send_message"))
async def handle_send_message_witout_arg(message: Message) -> None:
    await message.reply("Please provide user_id and text")

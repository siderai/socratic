from typing import Callable
from uuid import UUID

from pybotx import (
    Bot,
    BotAccount,
    BubbleMarkup,
    Button,
    Chat,
    ChatCreatedEvent,
    ChatCreatedMember,
    ChatTypes,
    IncomingMessage,
    UserKinds,
)


async def test_default_message_handler(
    bot: Bot,
    incoming_message_factory: Callable[..., IncomingMessage],
) -> None:
    # - Arrange -
    message = incoming_message_factory()

    # - Act -
    await bot.async_execute_bot_command(message)

    # - Assert -
    bot.answer_message.assert_awaited_once_with("Hello!")  # type: ignore


async def test_chat_created_handler(
    bot: Bot,
    bot_id: UUID,
    host: str,
) -> None:
    # - Arrange -
    command = ChatCreatedEvent(
        sync_id=UUID("2c1a31d6-f47f-5f54-aee2-d0c526bb1d54"),
        bot=BotAccount(
            id=bot_id,
            host=host,
        ),
        chat_name="Feature-party",
        chat=Chat(
            id=UUID("dea55ee4-7a9f-5da0-8c73-079f400ee517"),
            type=ChatTypes.GROUP_CHAT,
        ),
        creator_id=UUID("83fbf1c7-f14b-5176-bd32-ca15cf00d4b7"),
        members=[
            ChatCreatedMember(
                is_admin=True,
                huid=bot_id,
                username="Feature bot",
                kind=UserKinds.BOT,
            ),
            ChatCreatedMember(
                is_admin=False,
                huid=UUID("83fbf1c7-f14b-5176-bd32-ca15cf00d4b7"),
                username="Ivanov Ivan Ivanovich",
                kind=UserKinds.CTS_USER,
            ),
        ],
        raw_command=None,
    )

    # - Act -
    await bot.async_execute_bot_command(command)

    # - Assert -
    bot.answer_message.assert_awaited_once_with(  # type: ignore
        (
            "Вас приветствует Bot Example!\n\n"
            "Для более подробной информации нажмите кнопку `/help`"
        ),
        bubbles=BubbleMarkup([[Button(command="/help", label="/help")]]),
    )


async def test_help_handler(
    bot: Bot,
    incoming_message_factory: Callable[..., IncomingMessage],
) -> None:
    # - Arrange -
    message = incoming_message_factory(body="/help")

    # - Act -
    await bot.async_execute_bot_command(message)

    # - Assert -
    bot.answer_message.assert_awaited_once_with(  # type: ignore
        "`/help` -- Get available commands"
    )


async def test_git_commit_sha_handler(
    bot: Bot,
    incoming_message_factory: Callable[..., IncomingMessage],
) -> None:
    # - Arrange -
    message = incoming_message_factory(body="/_debug:git-commit-sha")

    # - Act -
    await bot.async_execute_bot_command(message)

    # - Assert -
    bot.answer_message.assert_awaited_once_with("<undefined>")  # type: ignore

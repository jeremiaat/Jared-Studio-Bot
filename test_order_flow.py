import asyncio
from unittest.mock import AsyncMock, MagicMock
from handlers.order import enter_description, skip_description, show_order_confirmation

async def test_enter_description():
    """Test entering a description and showing confirmation."""
    # Mock update and context
    update = MagicMock()
    update.message = MagicMock()
    update.message.text = "Test description"
    update.effective_chat.id = 123456

    context = MagicMock()
    context.user_data = {'order': {}}
    context.bot.send_message = AsyncMock()

    # Call the function
    result = await enter_description(update, context)

    # Assertions
    assert context.user_data['order']['description'] == "Test description"
    assert result == 6  # CONFIRM state
    context.bot.send_message.assert_called_once()
    print("test_enter_description passed")

async def test_skip_description():
    """Test skipping description and showing confirmation."""
    # Mock update and context
    update = MagicMock()
    update.callback_query = MagicMock()
    update.effective_chat.id = 123456

    context = MagicMock()
    context.user_data = {'order': {}}
    context.bot.send_message = AsyncMock()

    # Call the function
    result = await skip_description(update, context)

    # Assertions
    assert context.user_data['order']['description'] == ""
    assert result == 6  # CONFIRM state
    context.bot.send_message.assert_called_once()
    print("test_skip_description passed")

async def main():
    await test_enter_description()
    await test_skip_description()
    print("All tests passed!")

if __name__ == "__main__":
    asyncio.run(main())

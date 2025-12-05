import asyncio
import unittest
from unittest.mock import AsyncMock, MagicMock, patch
from telegram import Update, CallbackQuery, User, Chat, Message
from telegram.ext import ContextTypes
from handlers.price_catalog import list_prices, show_price_detail, _render_price, price_list_conversation

class TestPriceCatalog(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.user = User(id=12345, first_name="Test", is_bot=False)
        self.chat = Chat(id=12345, type="private")
        self.context = MagicMock(spec=ContextTypes.DEFAULT_TYPE)
        self.context.application.bot = MagicMock()
        member_mock = MagicMock()
        member_mock.status = "member"
        self.context.application.bot.get_chat_member = AsyncMock(return_value=member_mock)

    async def test_list_prices_non_member(self):
        """Test list_prices for non-member user"""
        # Mock callback query
        query = MagicMock(spec=CallbackQuery)
        query.from_user = self.user
        query.data = "price_list"
        query.message = MagicMock(spec=Message)
        query.message.chat_id = self.chat.id
        query.answer = AsyncMock()

        update = MagicMock(spec=Update)
        update.callback_query = query
        update.effective_chat = MagicMock(spec=Chat)
        update.effective_chat.id = self.chat.id
        update.effective_chat.send_message = AsyncMock()

        # Mock bot.get_chat_member to raise exception (non-member)
        self.context.application.bot.get_chat_member.side_effect = Exception("Not a member")

        # Call the function
        result = await list_prices(update, self.context)

        # Assertions
        self.assertEqual(result, -1)  # ConversationHandler.END
        update.effective_chat.send_message.assert_called_once()
        call_args = update.effective_chat.send_message.call_args
        self.assertIn("must be a member", call_args[0][0])
        query.answer.assert_called_once()

    async def test_list_prices_member_no_prices(self):
        """Test list_prices for member user with no prices"""
        # Mock callback query
        query = MagicMock(spec=CallbackQuery)
        query.from_user = self.user
        query.data = "price_list"
        query.message = MagicMock(spec=Message)
        query.message.chat_id = self.chat.id
        query.answer = AsyncMock()

        update = MagicMock(spec=Update)
        update.callback_query = query
        update.effective_chat = MagicMock(spec=Chat)
        update.effective_chat.id = self.chat.id
        update.effective_chat.send_message = AsyncMock()

        # Mock bot.get_chat_member to return member status
        member_mock = MagicMock()
        member_mock.status = "member"
        self.context.application.bot.get_chat_member.return_value = member_mock

        # Mock _render_price
        with patch('handlers.price_catalog._render_price', new_callable=AsyncMock) as mock_render:
            result = await list_prices(update, self.context)

            self.assertEqual(result, 1)  # SHOW_DETAIL = 1
            mock_render.assert_called_once_with(update, self.context, 0, force_new=False)
            query.answer.assert_called_once()

    async def test_show_price_detail_invalid_data(self):
        """Test show_price_detail with invalid callback data"""
        query = MagicMock(spec=CallbackQuery)
        query.from_user = self.user
        query.data = "invalid_data"
        query.message = MagicMock(spec=Message)
        query.answer = AsyncMock()
        query.edit_message_text = AsyncMock()

        update = MagicMock(spec=Update)
        update.callback_query = query

        # Mock bot.get_chat_member
        member_mock = MagicMock()
        member_mock.status = "member"
        self.context.application.bot.get_chat_member.return_value = member_mock

        result = await show_price_detail(update, self.context)

        # Should return None (no explicit return for invalid data)
        self.assertIsNone(result)
        query.edit_message_text.assert_called_with("Unknown selection.")

    async def test_render_price_no_drawings(self):
        """Test _render_price when no drawings are available"""
        update = MagicMock(spec=Update)
        update.callback_query = MagicMock(spec=CallbackQuery)
        update.callback_query.message = MagicMock(spec=Message)
        update.effective_message = MagicMock(spec=Message)

        update.callback_query.message.reply_text = AsyncMock()

        with patch('handlers.price_catalog.load_prices', return_value=[]):
            await _render_price(update, self.context, 0)

            update.callback_query.message.reply_text.assert_called_once_with("No price entries available.")

    async def test_render_price_with_drawings(self):
        """Test _render_price when drawings are available"""
        # Mock drawings
        mock_drawings = [
            {
                "category": "Portrait",
                "price": "$50",
                "size": "8x10",
                "description": "Beautiful portrait",
                "image": "http://example.com/image.jpg"
            }
        ]

        update = MagicMock(spec=Update)
        update.callback_query = MagicMock(spec=CallbackQuery)
        update.callback_query.message = MagicMock(spec=Message)
        update.effective_chat = self.chat
        update.callback_query.edit_message_media = AsyncMock()

        with patch('handlers.price_catalog.load_prices', return_value=mock_drawings):
            await _render_price(update, self.context, 0)

            update.callback_query.edit_message_media.assert_called_once()

if __name__ == '__main__':
    unittest.main()

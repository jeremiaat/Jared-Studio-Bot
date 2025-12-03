from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackQueryHandler, ConversationHandler, MessageHandler, filters
import json
import os
import logging
from utils.helpers import is_creator

logger = logging.getLogger(__name__)

ORDERS_FILE = 'orders.json'
PRICES_FILE = 'prices.json'

# Conversation states for creator management
(
    SELECTING_ACTION,
    ADDING_ITEM_CATEGORY,
    ADDING_ITEM_SIZE,
    ADDING_ITEM_PRICE,
    ADDING_ITEM_DESCRIPTION,
    ADDING_ITEM_IMAGE,
    EDITING_ITEM_SELECT,
    EDITING_ITEM_FIELD,
    EDITING_ITEM_VALUE,
    DELETING_ITEM,
    MANAGING_ORDER,
) = range(11)

def load_orders():
    """Load orders from JSON file"""
    if os.path.exists(ORDERS_FILE):
        try:
            with open(ORDERS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading orders: {e}")
    return []

def save_orders(orders):
    """Save orders to JSON file"""
    try:
        with open(ORDERS_FILE, 'w', encoding='utf-8') as f:
            json.dump(orders, f, indent=2, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Error saving orders: {e}")

def load_prices():
    """Load prices from JSON file"""
    if os.path.exists(PRICES_FILE):
        try:
            with open(PRICES_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading prices: {e}")
    return []

def save_prices(prices):
    """Save prices to JSON file"""
    try:
        with open(PRICES_FILE, 'w', encoding='utf-8') as f:
            json.dump(prices, f, indent=2, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Error saving prices: {e}")

async def view_orders(update, context):
    """View all available orders"""
    query = update.callback_query
    await query.answer()

    orders = load_orders()

    if not orders:
        message = "📋 No orders available."
    else:
        message = "📋 Available Orders:\n\n"
        for i, order in enumerate(orders, 1):
            message += f"{i}. Customer: @{order.get('customer_username', 'Unknown')}\n"
            message += f"   Size: {order.get('size', 'N/A')}\n"
            message += f"   Frame: {order.get('frame', 'N/A')}\n"
            message += f"   Delivery: {order.get('delivery_time', 'N/A')}\n"
            message += f"   Location: {order.get('location', 'N/A')}\n\n"

    keyboard = [
        [InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")]
    ]

    await query.edit_message_text(
        message,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def update_price(update, context):
    """Update price for a drawing"""
    query = update.callback_query
    await query.answer()

    prices = load_prices()

    if not prices:
        message = "No prices available to update."
    else:
        message = "Select a drawing to update price:\n\n"
        keyboard = []
        for i, price in enumerate(prices):
            keyboard.append([
                InlineKeyboardButton(
                    f"{price['category']} - {price['size']}: {price['price']}",
                    callback_data=f"update_price_{i}"
                )
            ])
        keyboard.append([InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")])

        await query.edit_message_text(
            message,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return

    keyboard = [[InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")]]
    await query.edit_message_text(
        message,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def add_catalogue(update, context):
    """Add new catalogue item"""
    query = update.callback_query
    await query.answer()

    message = "To add a new catalogue item, please provide the details in this format:\n\n"
    message += "Category: [category]\n"
    message += "Size: [size]\n"
    message += "Price: [price]\n"
    message += "Description: [description]\n"
    message += "Image URL: [url]\n\n"
    message += "Send this information as a message."

    keyboard = [[InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")]]
    await query.edit_message_text(
        message,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def creator_menu(update: Update, context):
    """Show creator management menu"""
    query = update.callback_query
    if query:
        await query.answer()

    message = "🎨 Creator Management Panel\n\n"
    message += "Choose an action:"

    keyboard = [
        [InlineKeyboardButton("📋 View Orders", callback_data="view_orders")],
        [InlineKeyboardButton("✏️ Edit Price Catalog", callback_data="edit_catalog")],
        [InlineKeyboardButton("➕ Add New Item", callback_data="add_new_item")],
        [InlineKeyboardButton("🗑️ Delete Item", callback_data="delete_item")],
        [InlineKeyboardButton("📊 Order Management", callback_data="manage_orders")],
        [InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")]
    ]

    if query:
        await query.edit_message_text(
            message,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    else:
        await update.effective_message.reply_text(
            message,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

async def edit_catalog(update: Update, context):
    """Show catalog editing options"""
    query = update.callback_query
    await query.answer()

    prices = load_prices()

    if not prices:
        message = "❌ No items in catalog to edit."
        keyboard = [[InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")]]
    else:
        message = "📝 Select an item to edit:\n\n"
        keyboard = []
        for i, item in enumerate(prices):
            keyboard.append([
                InlineKeyboardButton(
                    f"{item['category']} - {item['size']}",
                    callback_data=f"edit_item_{i}"
                )
            ])
        keyboard.append([InlineKeyboardButton("⬅️ Back to Creator Menu", callback_data="creator_menu")])

    await query.edit_message_text(
        message,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def edit_item_select(update: Update, context):
    """Show editing options for selected item"""
    query = update.callback_query
    await query.answer()

    data = query.data
    if not data.startswith("edit_item_"):
        return

    try:
        index = int(data.split("_", 2)[2])
    except ValueError:
        await query.edit_message_text("❌ Invalid item selection.")
        return

    prices = load_prices()
    if index >= len(prices):
        await query.edit_message_text("❌ Item not found.")
        return

    item = prices[index]
    context.user_data['editing_item_index'] = index

    message = f"✏️ Editing: {item['category']} - {item['size']}\n\n"
    message += "Current details:\n"
    message += f"• Category: {item['category']}\n"
    message += f"• Size: {item['size']}\n"
    message += f"• Price: {item['price']}\n"
    message += f"• Description: {item['description']}\n"
    message += f"• Image: {item['image']}\n\n"
    message += "What would you like to edit?"

    keyboard = [
        [InlineKeyboardButton("📝 Category", callback_data="edit_field_category")],
        [InlineKeyboardButton("📏 Size", callback_data="edit_field_size")],
        [InlineKeyboardButton("💰 Price", callback_data="edit_field_price")],
        [InlineKeyboardButton("📖 Description", callback_data="edit_field_description")],
        [InlineKeyboardButton("🖼️ Image URL", callback_data="edit_field_image")],
        [InlineKeyboardButton("⬅️ Back to Catalog", callback_data="edit_catalog")]
    ]

    await query.edit_message_text(
        message,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def edit_field_select(update: Update, context):
    """Handle field selection for editing"""
    query = update.callback_query
    await query.answer()

    data = query.data
    if not data.startswith("edit_field_"):
        return

    field = data.split("_", 2)[2]
    context.user_data['editing_field'] = field

    field_names = {
        'category': 'Category',
        'size': 'Size',
        'price': 'Price',
        'description': 'Description',
        'image': 'Image URL'
    }

    message = f"📝 Enter new {field_names.get(field, field)}:\n\n"
    message += "Send the new value as a message."

    keyboard = [[InlineKeyboardButton("❌ Cancel", callback_data="edit_catalog")]]
    await query.edit_message_text(
        message,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

    return EDITING_ITEM_VALUE

async def edit_field_value(update: Update, context):
    """Process the new field value"""
    user_data = context.user_data
    item_index = user_data.get('editing_item_index')
    field = user_data.get('editing_field')

    if item_index is None or field is None:
        await update.effective_message.reply_text("❌ Edit session expired. Please try again.")
        return ConversationHandler.END

    new_value = update.message.text.strip()
    if not new_value:
        await update.effective_message.reply_text("❌ Value cannot be empty. Please try again.")
        return EDITING_ITEM_VALUE

    prices = load_prices()
    if item_index >= len(prices):
        await update.effective_message.reply_text("❌ Item not found.")
        return ConversationHandler.END

    # Update the field
    prices[item_index][field] = new_value
    save_prices(prices)

    # Reload drawings to reflect changes
    import drawings
    drawings.drawings = drawings.load_prices()

    message = f"✅ Successfully updated {field}!\n\n"
    message += f"New {field}: {new_value}"

    keyboard = [
        [InlineKeyboardButton("📝 Edit Another Field", callback_data=f"edit_item_{item_index}")],
        [InlineKeyboardButton("📋 View Catalog", callback_data="edit_catalog")],
        [InlineKeyboardButton("🏠 Creator Menu", callback_data="creator_menu")]
    ]

    await update.effective_message.reply_text(
        message,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

    # Clear user data
    user_data.pop('editing_item_index', None)
    user_data.pop('editing_field', None)

    return ConversationHandler.END

async def add_new_item_start(update: Update, context):
    """Start adding a new catalog item"""
    query = update.callback_query
    await query.answer()

    message = "➕ Add New Catalog Item\n\n"
    message += "Please enter the category (e.g., 'Realistic Drawing', 'Anime Style', etc.):"

    keyboard = [[InlineKeyboardButton("❌ Cancel", callback_data="creator_menu")]]
    await query.edit_message_text(
        message,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

    return ADDING_ITEM_CATEGORY

async def add_item_category(update: Update, context):
    """Process category input"""
    category = update.message.text.strip()
    if not category:
        await update.effective_message.reply_text("❌ Category cannot be empty. Please enter a category:")
        return ADDING_ITEM_CATEGORY

    context.user_data['new_item'] = {'category': category}

    message = f"✅ Category: {category}\n\n"
    message += "Now enter the size (e.g., 'A4', 'A3', '8x10 inches', etc.):"

    keyboard = [[InlineKeyboardButton("❌ Cancel", callback_data="creator_menu")]]
    await update.effective_message.reply_text(
        message,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

    return ADDING_ITEM_SIZE

async def add_item_size(update: Update, context):
    """Process size input"""
    size = update.message.text.strip()
    if not size:
        await update.effective_message.reply_text("❌ Size cannot be empty. Please enter a size:")
        return ADDING_ITEM_SIZE

    context.user_data['new_item']['size'] = size

    message = f"✅ Size: {size}\n\n"
    message += "Now enter the price (e.g., '400-600 ETB', '$25-35', etc.):"

    keyboard = [[InlineKeyboardButton("❌ Cancel", callback_data="creator_menu")]]
    await update.effective_message.reply_text(
        message,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

    return ADDING_ITEM_PRICE

async def add_item_price(update: Update, context):
    """Process price input"""
    price = update.message.text.strip()
    if not price:
        await update.effective_message.reply_text("❌ Price cannot be empty. Please enter a price:")
        return ADDING_ITEM_PRICE

    context.user_data['new_item']['price'] = price

    message = f"✅ Price: {price}\n\n"
    message += "Now enter the description:"

    keyboard = [[InlineKeyboardButton("❌ Cancel", callback_data="creator_menu")]]
    await update.effective_message.reply_text(
        message,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

    return ADDING_ITEM_DESCRIPTION

async def add_item_description(update: Update, context):
    """Process description input"""
    description = update.message.text.strip()
    if not description:
        await update.effective_message.reply_text("❌ Description cannot be empty. Please enter a description:")
        return ADDING_ITEM_DESCRIPTION

    context.user_data['new_item']['description'] = description

    message = f"✅ Description: {description}\n\n"
    message += "Finally, enter the image URL:"

    keyboard = [[InlineKeyboardButton("❌ Cancel", callback_data="creator_menu")]]
    await update.effective_message.reply_text(
        message,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

    return ADDING_ITEM_IMAGE

async def add_item_image(update: Update, context):
    """Process image URL input and save the item"""
    image_url = update.message.text.strip()
    if not image_url:
        await update.effective_message.reply_text("❌ Image URL cannot be empty. Please enter an image URL:")
        return ADDING_ITEM_IMAGE

    # Get the new item data
    new_item = context.user_data.get('new_item', {})
    new_item['image'] = image_url

    # Load current prices and add new item
    prices = load_prices()
    prices.append(new_item)
    save_prices(prices)

    # Reload drawings to reflect changes
    import drawings
    drawings.drawings = drawings.load_prices()

    message = "✅ New item added successfully!\n\n"
    message += f"🎨 Category: {new_item['category']}\n"
    message += f"📏 Size: {new_item['size']}\n"
    message += f"💰 Price: {new_item['price']}\n"
    message += f"📖 Description: {new_item['description']}\n"
    message += f"🖼️ Image: {new_item['image']}"

    keyboard = [
        [InlineKeyboardButton("➕ Add Another Item", callback_data="add_new_item")],
        [InlineKeyboardButton("📋 View Catalog", callback_data="edit_catalog")],
        [InlineKeyboardButton("🏠 Creator Menu", callback_data="creator_menu")]
    ]

    await update.effective_message.reply_text(
        message,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

    # Clear user data
    context.user_data.pop('new_item', None)

    return ConversationHandler.END

async def delete_item_select(update: Update, context):
    """Show items available for deletion"""
    query = update.callback_query
    await query.answer()

    prices = load_prices()

    if not prices:
        message = "❌ No items in catalog to delete."
        keyboard = [[InlineKeyboardButton("🏠 Creator Menu", callback_data="creator_menu")]]
    else:
        message = "🗑️ Select an item to delete:\n\n"
        keyboard = []
        for i, item in enumerate(prices):
            keyboard.append([
                InlineKeyboardButton(
                    f"❌ {item['category']} - {item['size']}",
                    callback_data=f"confirm_delete_{i}"
                )
            ])
        keyboard.append([InlineKeyboardButton("⬅️ Back to Creator Menu", callback_data="creator_menu")])

    await query.edit_message_text(
        message,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def confirm_delete_item(update: Update, context):
    """Confirm deletion of selected item"""
    query = update.callback_query
    await query.answer()

    data = query.data
    if not data.startswith("confirm_delete_"):
        return

    try:
        index = int(data.split("_", 2)[2])
    except ValueError:
        await query.edit_message_text("❌ Invalid item selection.")
        return

    prices = load_prices()
    if index >= len(prices):
        await query.edit_message_text("❌ Item not found.")
        return

    item = prices[index]

    message = "⚠️ Confirm Deletion\n\n"
    message += f"Are you sure you want to delete:\n\n"
    message += f"🎨 {item['category']} - {item['size']}\n"
    message += f"💰 {item['price']}\n\n"
    message += "This action cannot be undone!"

    keyboard = [
        [InlineKeyboardButton("✅ Yes, Delete", callback_data=f"execute_delete_{index}")],
        [InlineKeyboardButton("❌ No, Cancel", callback_data="delete_item")]
    ]

    await query.edit_message_text(
        message,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def execute_delete_item(update: Update, context):
    """Execute the deletion of selected item"""
    query = update.callback_query
    await query.answer()

    data = query.data
    if not data.startswith("execute_delete_"):
        return

    try:
        index = int(data.split("_", 2)[2])
    except ValueError:
        await query.edit_message_text("❌ Invalid item selection.")
        return

    prices = load_prices()
    if index >= len(prices):
        await query.edit_message_text("❌ Item not found.")
        return

    deleted_item = prices.pop(index)
    save_prices(prices)

    # Reload drawings to reflect changes
    import drawings
    drawings.drawings = drawings.load_prices()

    message = "✅ Item deleted successfully!\n\n"
    message += f"Deleted: {deleted_item['category']} - {deleted_item['size']}"

    keyboard = [
        [InlineKeyboardButton("🗑️ Delete Another", callback_data="delete_item")],
        [InlineKeyboardButton("📋 View Catalog", callback_data="edit_catalog")],
        [InlineKeyboardButton("🏠 Creator Menu", callback_data="creator_menu")]
    ]

    await query.edit_message_text(
        message,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def manage_orders(update: Update, context):
    """Show order management options"""
    query = update.callback_query
    await query.answer()

    orders = load_orders()

    if not orders:
        message = "📋 No orders available for management."
        keyboard = [[InlineKeyboardButton("🏠 Creator Menu", callback_data="creator_menu")]]
    else:
        message = "📊 Order Management\n\n"
        message += "Select an order to manage:\n\n"

        keyboard = []
        for i, order in enumerate(orders):
            status = order.get('status', 'pending')
            customer = order.get('customer_username', 'Unknown')
            keyboard.append([
                InlineKeyboardButton(
                    f"#{i+1} @{customer} ({status})",
                    callback_data=f"manage_order_{i}"
                )
            ])
        keyboard.append([InlineKeyboardButton("⬅️ Back to Creator Menu", callback_data="creator_menu")])

    await query.edit_message_text(
        message,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def manage_order_details(update: Update, context):
    """Show details and management options for selected order"""
    query = update.callback_query
    await query.answer()

    data = query.data
    if not data.startswith("manage_order_"):
        return

    try:
        index = int(data.split("_", 2)[2])
    except ValueError:
        await query.edit_message_text("❌ Invalid order selection.")
        return

    orders = load_orders()
    if index >= len(orders):
        await query.edit_message_text("❌ Order not found.")
        return

    order = orders[index]
    context.user_data['managing_order_index'] = index

    message = f"📋 Order #{index+1} Details\n\n"
    message += f"👤 Customer: @{order.get('customer_username', 'Unknown')}\n"
    message += f"📏 Size: {order.get('size', 'N/A')}\n"
    message += f"🖼️ Frame: {order.get('frame', 'N/A')}\n"
    message += f"⏰ Delivery: {order.get('delivery_time', 'N/A')}\n"
    message += f"📍 Location: {order.get('location', 'N/A')}\n"
    message += f"📝 Description: {order.get('description', 'N/A')}\n"
    message += f"📅 Status: {order.get('status', 'pending').title()}\n\n"
    message += "Choose an action:"

    keyboard = [
        [InlineKeyboardButton("✅ Mark as Completed", callback_data="order_complete")],
        [InlineKeyboardButton("🔄 Update Status", callback_data="order_update_status")],
        [InlineKeyboardButton("📞 Contact Customer", callback_data=f"contact_customer_{index}")],
        [InlineKeyboardButton("⬅️ Back to Orders", callback_data="manage_orders")]
    ]

    await query.edit_message_text(
        message,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def order_complete(update: Update, context):
    """Mark order as completed"""
    query = update.callback_query
    await query.answer()

    order_index = context.user_data.get('managing_order_index')
    if order_index is None:
        await query.edit_message_text("❌ Order session expired.")
        return

    orders = load_orders()
    if order_index >= len(orders):
        await query.edit_message_text("❌ Order not found.")
        return

    orders[order_index]['status'] = 'completed'
    save_orders(orders)

    message = "✅ Order marked as completed!\n\n"
    message += "The customer will be notified of the completion."

    keyboard = [
        [InlineKeyboardButton("📋 Manage Another Order", callback_data="manage_orders")],
        [InlineKeyboardButton("🏠 Creator Menu", callback_data="creator_menu")]
    ]

    await query.edit_message_text(
        message,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

    context.user_data.pop('managing_order_index', None)

# Create handlers
view_orders_handler = CallbackQueryHandler(view_orders, pattern="^view_orders$")
update_price_handler = CallbackQueryHandler(update_price, pattern="^update_price$")
add_catalogue_handler = CallbackQueryHandler(add_catalogue, pattern="^add_catalogue$")

# New handlers for comprehensive creator management
creator_menu_handler = CallbackQueryHandler(creator_menu, pattern="^creator_menu$")
edit_catalog_handler = CallbackQueryHandler(edit_catalog, pattern="^edit_catalog$")
edit_item_handler = CallbackQueryHandler(edit_item_select, pattern="^edit_item_\\d+$")
edit_field_handler = CallbackQueryHandler(edit_field_select, pattern="^edit_field_\\w+$")
add_new_item_handler = CallbackQueryHandler(add_new_item_start, pattern="^add_new_item$")
delete_item_handler = CallbackQueryHandler(delete_item_select, pattern="^delete_item$")
confirm_delete_handler = CallbackQueryHandler(confirm_delete_item, pattern="^confirm_delete_\\d+$")
execute_delete_handler = CallbackQueryHandler(execute_delete_item, pattern="^execute_delete_\\d+$")
manage_orders_handler = CallbackQueryHandler(manage_orders, pattern="^manage_orders$")
manage_order_handler = CallbackQueryHandler(manage_order_details, pattern="^manage_order_\\d+$")
order_complete_handler = CallbackQueryHandler(order_complete, pattern="^order_complete$")

# Conversation handler for adding new items
add_item_conversation = ConversationHandler(
    entry_points=[add_new_item_handler],
    states={
        ADDING_ITEM_CATEGORY: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_item_category)],
        ADDING_ITEM_SIZE: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_item_size)],
        ADDING_ITEM_PRICE: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_item_price)],
        ADDING_ITEM_DESCRIPTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_item_description)],
        ADDING_ITEM_IMAGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_item_image)],
    },
    fallbacks=[CallbackQueryHandler(lambda u, c: ConversationHandler.END, pattern="^creator_menu$")],
    per_message=True,
)

# Conversation handler for editing items
edit_item_conversation = ConversationHandler(
    entry_points=[edit_field_handler],
    states={
        EDITING_ITEM_VALUE: [MessageHandler(filters.TEXT & ~filters.COMMAND, edit_field_value)],
    },
    fallbacks=[CallbackQueryHandler(lambda u, c: ConversationHandler.END, pattern="^edit_catalog$")],
    per_message=True,
)

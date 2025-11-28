
# TODO: Add Role-Based Functionality to Jared_Studi_Bot

- [x] Implement role-based access control (Creator vs Users)
- [x] Add creator identification via user ID
- [x] Create role-appropriate menus (Creator: management options, Users: ordering options)
- [x] Prevent creators from placing orders
- [x] Add storage for orders and prices (JSON files)
- [x] Create creator management handlers (view_orders, update_price, add_catalogue)
- [x] Update drawings.py to load prices from storage
- [x] Remove main menu button from order confirmation
- [x] Update bot.py to include new handlers
- [x] Test role-based functionality
- [x] Add role checks to all handlers to prevent unauthorized access
- [x] Prevent creators from viewing price list

# TODO: Implement Role-Based Functionality

- [x] Add creator user ID to config.py
- [x] Create utils/helpers.py with role checking function
- [x] Create storage files: orders.json and prices.json
- [x] Modify handlers/start.py for role-appropriate menus
- [x] Modify handlers/order.py to prevent creators from ordering
- [x] Create handlers/creator.py for view_orders, update_price, add_catalogue
- [x] Update bot.py to add creator handlers
- [x] Update drawings.py to load prices from storage
- [x] Remove main menu button from order successful message
- [x] Test role-based functionality

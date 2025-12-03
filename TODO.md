# TODO: Fix PTBUserWarnings and Next Button Issue

## Issues to Fix
- [x] PTBUserWarnings: Multiple ConversationHandler instances have `per_message=False`
- [x] Next button in price list catalogue not working

## Files to Update
- [x] handlers/order.py: Update order_conversation per_message=False to True
- [x] handlers/creator.py: Update add_item_conversation and edit_item_conversation per_message=False to True
- [x] bot.py: Update price_list_conversation to add per_message=True

## Testing
- [ ] Test price list navigation (next/prev buttons)
- [ ] Verify no more PTBUserWarnings in logs

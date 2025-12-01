import json
from api.webhook import handler

# Mock event for POST request
mock_event = {
    'httpMethod': 'POST',
    'body': json.dumps({
        'update_id': 123456789,
        'message': {
            'message_id': 1,
            'from': {'id': 123456, 'is_bot': False, 'first_name': 'Test'},
            'chat': {'id': 123456, 'type': 'private'},
            'date': 1609459200,
            'text': '/start'
        }
    })
}

# Mock context
mock_context = {}

try:
    response = handler(mock_event, mock_context)
    print("Handler response:", response)
    print("Test passed: Handler executed without errors")
except Exception as e:
    print(f"Test failed: {e}")

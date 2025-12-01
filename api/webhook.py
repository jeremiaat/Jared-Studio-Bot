from telegram import Update
from bot import application
import json

def handler(event, context):
    if event['httpMethod'] != 'POST':
        return {
            'statusCode': 405,
            'body': 'Method Not Allowed'
        }

    try:
        update_data = json.loads(event['body'])
        update = Update.de_json(update_data, application.bot)
        application.process_update(update)
        return {
            'statusCode': 200,
            'body': 'OK'
        }
    except Exception as e:
        print(f"Error processing update: {e}")
        return {
            'statusCode': 500,
            'body': 'Internal Server Error'
        }

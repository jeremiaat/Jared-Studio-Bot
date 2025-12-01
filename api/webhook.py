from telegram import Update
from bot import application
import json
import logging
import asyncio

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def handler(event, context):
    logger.info(f"Received event: {event['httpMethod']}")
    if event['httpMethod'] != 'POST':
        return {
            'statusCode': 405,
            'body': 'Method Not Allowed'
        }

    try:
        update_data = json.loads(event['body'])
        logger.info(f"Update data: {update_data}")
        update = Update.de_json(update_data, application.bot)
        logger.info("Processing update...")
        await application.process_update(update)
        logger.info("Update processed successfully")
        return {
            'statusCode': 200,
            'body': 'OK'
        }
    except Exception as e:
        logger.error(f"Error processing update: {e}", exc_info=True)
        return {
            'statusCode': 500,
            'body': 'Internal Server Error'
        }

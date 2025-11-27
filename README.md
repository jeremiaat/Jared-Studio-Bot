# Jared Drawing Studio Telegram Bot

A Telegram bot for Jared Drawing Studio that showcases artwork and handles customer inquiries.

## Features

- Channel membership verification (@Jaredrawing)
- Interactive price list with image navigation
- Order placement functionality
- Membership status logging

## Setup

### Prerequisites

- Python 3.8 or higher
- Telegram Bot Token (get from [@BotFather](https://t.me/botfather))
- Channel admin access for membership verification

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd jared-drawing-bot
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file (copy from `.env.example`):
```bash
cp .env.example .env
```

5. Edit `.env` and add your bot token:
```
BOT_TOKEN=your_telegram_bot_token_here
```

## Getting Your Bot Token

1. Message [@BotFather](https://t.me/botfather) on Telegram
2. Send `/newbot` and follow the instructions
3. Copy the token and paste it in your `.env` file

## Channel Setup

1. Create or have admin access to the channel @Jaredrawing
2. Add your bot as an administrator to the channel
3. The bot will verify membership before showing the price list

## Usage

### Local Development

Run the bot locally:
```bash
python bot.py
```

### Deployment

#### Heroku

1. Create a new Heroku app
2. Set the environment variable `BOT_TOKEN` in Heroku dashboard
3. Deploy using Heroku CLI:
```bash
heroku create your-app-name
git push heroku main
```

#### Railway

1. Connect your GitHub repository to Railway
2. Add the `BOT_TOKEN` environment variable in Railway dashboard
3. Deploy automatically

#### Render

1. Connect your GitHub repository to Render
2. Create a new service and select "Background Worker" (not "Web Service")
3. Set the build command: `pip install -r requirements.txt`
4. Set the start command: `python bot.py`
5. Add the `BOT_TOKEN` environment variable in Render dashboard
6. Deploy

Alternatively, if using `render.yaml` for configuration:
1. Ensure `render.yaml` is in your repository root
2. Connect your GitHub repository to Render
3. Render will automatically detect the configuration
4. Add the `BOT_TOKEN` environment variable in Render dashboard
5. Deploy

#### Other Platforms

The bot can be deployed on any platform that supports Python applications:

- **VPS/Server**: Use systemd or screen to run `python bot.py`
- **Docker**: Create a Dockerfile and deploy to container platforms
- **AWS/GCP/Azure**: Use their serverless or VM services

## Bot Commands

- `/start` - Initialize the bot and check channel membership
- Interactive buttons for navigation and ordering

## Project Structure

```
├── bot.py                 # Main bot application
├── handlers/
│   ├── start.py          # Start and membership handlers
│   └── navigation.py     # Drawing navigation handlers
├── drawings.py           # Drawing data and utilities
├── utils/
│   ├── helpers.py        # Helper functions
│   └── messages.py       # Message templates
├── public/images/        # Image assets
├── requirements.txt      # Python dependencies
├── Procfile             # Heroku deployment
├── runtime.txt          # Python version for Heroku
└── .env.example         # Environment variables template
```

## Monitoring

The bot logs membership status checks to the console. In production, monitor these logs to track user engagement and bot health.

## License

MIT License

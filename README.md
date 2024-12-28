# QuizBot

QuizBot is a Telegram bot that allows users to participate in quizzes directly from Telegram. Built using the `python-telegram-bot` library, it supports creating multiple-choice questions and evaluating user responses in real-time.

## Features

- Create and manage quizzes with multiple-choice questions.
- Evaluate responses automatically.
- Store quiz questions in a customizable format.
- Easily extendable to include new features.

## Prerequisites

Before running QuizBot, ensure you have the following:

- **Python 3.8 or higher**
- A Telegram bot token from [BotFather](https://core.telegram.org/bots#botfather)
- Libraries listed in `requirements.txt`

## Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/tusharpamnani/QuizBot.git
cd QuizBot
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure the Bot Token

- Open the `app.py` file.
- Replace the placeholder `your_telegram_bot_token` with your Telegram bot token.

```python
TOKEN = "your_telegram_bot_token"
```

### 4. Run the Bot

```bash
python app.py
```

### 5. Interact with the Bot

- Start a chat with your bot on Telegram.
- The bot will guide you through using its features.

## Deployment

To run the bot 24/7, deploy it using one of the following options:

### Heroku
1. Create a `Procfile`:
   ```
   worker: python app.py
   ```
2. Push the code to Heroku.

### Railway
1. Create a new project on [Railway](https://railway.app/).
2. Connect your GitHub repository.
3. Add environment variables and deploy.

### VPS
1. Copy the bot files to your server.
2. Run the bot using:
   ```bash
   nohup python app.py &
   ```

## Technologies Used

- [Python](https://www.python.org/)
- [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot)
- [httpx](https://www.python-httpx.org/)

## Contributing

Contributions are welcome! Feel free to:

- Report bugs
- Suggest features
- Submit pull requests

To contribute:
1. Fork the repository.
2. Create a new branch for your feature/bug fix.
3. Commit your changes and create a pull request.

## License

This project is licensed under the [MIT License](LICENSE).

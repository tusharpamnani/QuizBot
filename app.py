import os
import logging
from telegram import Update, Poll, Bot
from telegram.ext import Application, CommandHandler, ContextTypes, PollHandler
from datetime import datetime, timedelta
import google.generativeai as genai
import asyncio
from collections import defaultdict

# Configure logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure your API keys
TELEGRAM_TOKEN = "7896809312:AAGKL9GoBMLN-OtnMi6K3CeLcf5R3MDgvaY"
GEMINI_API_KEY = "AIzaSyD6Hv0XHxY3g04r3AVgR4o8xAoaTp2duRQ"

# Configure Gemini
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

class QuizBot:
    def __init__(self):
        self.current_quiz = {}  # Store quiz state for each group
        self.user_scores = defaultdict(lambda: defaultdict(int))  # Group -> User -> Score
        self.questions_count = defaultdict(int)  # Track number of questions per group

    async def generate_question(self, topic):
        """Generate a quiz question using Gemini API with improved error handling."""
        prompt = f"""Generate a multiple choice question about {topic}.
        Your response must be in exactly this format:
        Question: [your question]
        Correct Answer: [the correct option]
        Option 1: [first option]
        Option 2: [second option]
        Option 3: [third option]
        Option 4: [fourth option]
        
        The correct answer must be exactly the same as one of the options."""
        
        try:
            response = model.generate_content(prompt)
            response_text = response.text.strip()
            
            # Parse the response
            lines = response_text.split('\n')
            lines = [line.strip() for line in lines if line.strip()]
            
            question = None
            correct_answer = None
            options = []
            
            for line in lines:
                if line.startswith('Question:'):
                    question = line.replace('Question:', '').strip()
                elif line.startswith('Correct Answer:'):
                    correct_answer = line.replace('Correct Answer:', '').strip()
                elif line.startswith('Option'):
                    option = line.split(':', 1)[1].strip()
                    options.append(option)
            
            if not question or not correct_answer or len(options) != 4:
                raise ValueError("Invalid response format from AI")
            
            if correct_answer not in options:
                raise ValueError("Correct answer doesn't match any option")
            
            return question, correct_answer, options
        
        except Exception as e:
            logger.error(f"Error generating question for topic {topic}: {e}")
            
            # Backup question
            return (
                "What is the capital of France?",
                "Paris",
                ["London", "Paris", "Berlin", "Madrid"]
            )

    async def start_quiz(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Start a new quiz session immediately."""
        if not context.args:
            await update.message.reply_text(
                "Please provide a topic for the quiz!\nExample: /startquiz Python Programming"
            )
            return

        chat_id = update.message.chat_id
        topic = " ".join(context.args)
        
        if chat_id in self.current_quiz:
            await update.message.reply_text("A quiz is already running in this group! Please wait for it to complete.")
            return
        
        self.current_quiz[chat_id] = {
            "topic": topic,
            "questions_asked": 0,
            "correct_answers": [],
            "participants": defaultdict(int)
        }
        
        await update.message.reply_text(
            f"📢 Starting quiz on {topic}!\n"
            "5 questions will be posted every 30 minutes.\n"
            "Get ready to participate! 🎯\n\n"
            "First question coming up in 10 seconds..."
        )
        await asyncio.sleep(10)
        await self.send_quiz_question(chat_id, context.bot)

    async def send_quiz_question(self, chat_id: int, bot: Bot):
        """Send a quiz question to the group."""
        quiz_state = self.current_quiz.get(chat_id)
        if not quiz_state:
            return

        try:
            question, correct_answer, options = await self.generate_question(quiz_state["topic"])
            correct_index = options.index(correct_answer)

            # Corrected send_poll usage
            message = await bot.send_poll(
                chat_id=chat_id,
                question=question,
                options=options,
                type="quiz",
                correct_option_id=correct_index,
                is_anonymous=False,
                explanation="Let's see who gets this right!",
            )


            quiz_state["correct_answers"].append(correct_index)
            quiz_state["questions_asked"] += 1

            if quiz_state["questions_asked"] < 5:
                await bot.send_message(chat_id, f"Next question in 30 minutes.")
                await asyncio.sleep(1800)  # Wait 30 minutes
                await self.send_quiz_question(chat_id, bot)
            else:
                await self.announce_winner(chat_id, bot)

        except Exception as e:
            logger.error(f"Error in send_quiz_question: {e}")
            await bot.send_message(chat_id, "There was an error generating the question. Trying again...")
            await asyncio.sleep(5)
            await self.send_quiz_question(chat_id, bot)

    async def handle_answer(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle answers to quiz questions."""
        poll_answer = update.poll_answer
        chat_id = context.bot_data.get(poll_answer.poll_id)
        
        if chat_id:
            quiz_state = self.current_quiz.get(chat_id)
            if quiz_state:
                user_id = poll_answer.user.id
                if poll_answer.option_ids[0] == quiz_state["correct_answers"][-1]:
                    quiz_state["participants"][user_id] += 1

    async def announce_winner(self, chat_id: int, bot: Bot):
        """Announce the winner of the quiz."""
        quiz_state = self.current_quiz.pop(chat_id, None)
        if not quiz_state["participants"]:
            await bot.send_message(chat_id, "No participants in this quiz!")
            return

        max_score = max(quiz_state["participants"].values())
        winners = [uid for uid, score in quiz_state["participants"].items() if score == max_score]

        text = f"🎉 Quiz completed!\n\n"
        if len(winners) == 1:
            text += f"The winner is {winners[0]} with {max_score} correct answers!"
        else:
            text += f"Multiple winners with {max_score} correct answers!"

        await bot.send_message(chat_id, text)

def main():
    quiz_bot = QuizBot()
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    application.add_handler(CommandHandler("startquiz", quiz_bot.start_quiz))
    application.add_handler(PollHandler(quiz_bot.handle_answer))
    application.run_polling()

if __name__ == "__main__":
    main()

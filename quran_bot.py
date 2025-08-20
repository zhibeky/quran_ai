import json
import logging
import os
from typing import Dict, Any
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from minsearch import AppendableIndex
from openai import OpenAI

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class QuranRAGBot:
    def __init__(self):
        self.index = None
        self.client = None
        self.documents = None
        self.setup_rag_system()
        
    def setup_rag_system(self):
        """Initialize the RAG system with Quran data and OpenAI client"""
        try:
            # Load Quran data
            with open("quran_with_tafsir.json", "r", encoding="utf-8") as f:
                self.documents = json.load(f)
            
            # Initialize search index
            self.index = AppendableIndex(
                text_fields=["question", "text", "section"],
                keyword_fields=["surah_number", "surah_name", "surah_translation", "ayah_number", "reference", "text", "language", "tafsir_text", "tafsir_source"]
            )
            self.index.fit(self.documents)
            
            # Initialize OpenAI client
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY not found in environment variables")
            self.client = OpenAI(api_key=api_key)
            
            logger.info("RAG system initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize RAG system: {e}")
            raise
    
    def search(self, query: str) -> list:
        """Search the Quran index for relevant passages"""
        boost = {'question': 3.0, 'section': 0.5}
        
        results = self.index.search(
            query=query,
            boost_dict=boost,
            num_results=5,
            output_ids=True
        )
        
        return results
    
    def build_prompt(self, query: str, search_results: list) -> str:
        """Build the prompt for the LLM using search results"""
        prompt_template = """
You are an Imam and a teacher of the Qur'an. 
Answer the QUESTION using only the CONTEXT provided (which contains Qur'an verses and tafsir). 
Do not add information that is not in the CONTEXT. 
If the answer cannot be found in the CONTEXT, say you do not know.

When answering:
- Use clear, respectful, and simple language. 
- Quote directly from the Qur'an or tafsir when relevant. 
- Always include the surah and ayah reference (e.g., Surah Al-Fatiha 1:5).
- If the Qur'an text alone does not fully answer the QUESTION and you use tafsir (explanatory commentary) to clarify, explicitly label it as 'Tafsir clarification'.

Format your answer exactly like this:

Qur'an evidence:
<quote Quran verses used>

Tafsir clarification (if needed):
<quote tafsir used or write 'Not needed' if Quran text is enough>

Conclusion:
<Your answer in clear, concise language>

<QUESTION>
{question}
</QUESTION>

<CONTEXT>
{context}
</CONTEXT>

<ANSWER>
""".strip()
        
        context = ""
        for doc in search_results:
            context = context + f"surah_name: {doc['surah_name']}\nreference: {doc['reference']}\nquestion: {query}\nquran_text: {doc['text']}\ntafsir: {doc['tafsir_text']}\n\n"
        
        prompt = prompt_template.format(question=query, context=context).strip()
        return prompt
    
    def get_llm_response(self, prompt: str) -> str:
        """Get response from OpenAI LLM"""
        try:
            response = self.client.chat.completions.create(
                model='gpt-4o-mini',
                messages=[{"role": "user", "content": prompt}]
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"LLM API call failed: {e}")
            return "I apologize, but I'm experiencing technical difficulties. Please try again later."
    
    def rag_query(self, query: str) -> str:
        """Perform RAG query: search + LLM response"""
        try:
            search_results = self.search(query)
            prompt = self.build_prompt(query, search_results)
            answer = self.get_llm_response(prompt)
            return answer
        except Exception as e:
            logger.error(f"RAG query failed: {e}")
            return "I apologize, but I encountered an error while processing your question. Please try again."

# Initialize the bot
quran_bot = QuranRAGBot()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    welcome_message = """
🕌 *Welcome to the Quran AI Assistant!*

I'm here to help you find answers to your questions about the Quran using authentic sources and tafsir (explanatory commentary).

*How to use me:*
• Simply ask me any question about the Quran
• I'll search through the Quran and tafsir to provide you with accurate answers
• Always include relevant Quran verses and references

*Example questions:*
• "What does the Quran say about patience?"
• "Tell me about the story of Prophet Yusuf"
• "What are the benefits of reading the Quran?"

*Commands:*
/start - Show this welcome message
/help - Show help information
/about - Learn more about this bot

May Allah guide us all to the right path. 🤲
"""
    
    await update.message.reply_text(welcome_message, parse_mode='Markdown')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    help_text = """
📚 *Quran AI Assistant Help*

*How to ask questions:*
Simply type your question in natural language. For example:
• "What does the Quran say about kindness?"
• "Tell me about the five pillars of Islam"
• "What are the benefits of prayer?"

*What I provide:*
• Direct quotes from the Quran with surah and ayah references
• Tafsir (explanatory commentary) when relevant
• Clear, concise answers based on authentic sources

*Tips for better answers:*
• Be specific in your questions
• Ask about topics, stories, or concepts in the Quran
• I can help with both simple and complex theological questions

*Note:* I only provide information that can be found in the Quran and authentic tafsir sources.

Need help? Just ask! 🤔
"""
    
    await update.message.reply_text(help_text, parse_mode='Markdown')

async def about(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send information about the bot."""
    about_text = """
🤖 *About Quran AI Assistant*

*What I am:*
I'm an AI-powered assistant that helps you find answers to questions about the Quran using a Retrieval-Augmented Generation (RAG) system.

*How I work:*
1. I search through a comprehensive database of Quran verses and tafsir
2. I use advanced AI to understand your question
3. I provide answers based on authentic Islamic sources
4. I always include proper references and citations

*My sources:*
• The Holy Quran (multiple translations)
• Tafsir Ibn Kathir and other authentic commentaries
• Verified Islamic scholarship

*Important note:*
While I strive for accuracy, I'm a tool to help with learning and reference. For complex religious matters, always consult with qualified Islamic scholars.

*Technology:*
Built with modern AI technology, including OpenAI's language models and advanced search algorithms.

May this tool help you in your journey of learning and understanding the Quran. 📖✨
"""
    
    await update.message.reply_text(about_text, parse_mode='Markdown')

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle incoming messages and provide Quran RAG responses."""
    user_message = update.message.text
    
    # Send typing indicator
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    
    # Get response from RAG system
    response = quran_bot.rag_query(user_message)
    
    # Send response
    await update.message.reply_text(response, parse_mode='Markdown')

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)

def main() -> None:
    """Start the bot."""
    # Get bot token from environment
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        logger.error("TELEGRAM_BOT_TOKEN not found in environment variables")
        return
    
    # Create the Application
    application = Application.builder().token(token).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("about", about))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Add error handler
    application.add_error_handler(error_handler)
    
    # Start the bot
    logger.info("Starting Quran AI Assistant bot...")
    application.run_polling()

if __name__ == '__main__':
    main()

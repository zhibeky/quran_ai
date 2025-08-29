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
    
    def build_context(self, search_results: list) -> str:
        """Build context from search results"""
        context = ""
        for doc in search_results:
            context = context + f"surah_name: {doc['surah_name']}\nreference: {doc['reference']}\nquran_text: {doc['text']}\ntafsir: {doc['tafsir_text']}\n\n"
        return context
    
    def get_agentic_prompt_template(self) -> str:
        """Get the agentic prompt template"""
        return """
You are an Imam and a teacher of the QURAN.

You're given a QUESTION from a person and that you need to answer with provided CONTEXT. And if there is no CONTEXT you can use your own knowledge.
At the beginning the context is EMPTY.

The CONTEXT is build with the QURAN and documents of TAFSIR.
SEARCH_QUERIES contains the queries that were used to retrieve the documents from QURAN to and add them to the context.
PREVIOUS_ACTIONS contains the actions you already performed.

At the beginning the CONTEXT is empty.

When answering:
- Use clear, respectful, and simple language. 
- Quote directly from the Qur'an or tafsir when relevant. 
- Always include the surah and ayah reference (e.g., Surah Al-Fatiha 1:5).
- If the Qur'an text alone does not fully answer the QUESTION and you use tafsir (explanatory commentary) to clarify, explicitly label it as 'Tafsir clarification'.

You can perform the following actions:

- Search in the QURAN and TAFSIR database to get more data for the CONTEXT
- Answer the question using the CONTEXT
- Answer the question using your own knowledge

For the SEARCH action, build search requests based on the CONTEXT and the QUESTION.
Carefully analyze the CONTEXT and generate the requests to deeply explore the topic. 

Don't use search queries used at the previous iterations.

Don't repeat previously performed actions.

Don't perform more than {max_iterations} iterations for a given student question.
The current iteration number: {iteration_number}. If we exceed the allowed number 
of iterations, give the best possible answer with the provided information.

Output templates:

If you want to perform search, use this template:

{{
"action": "SEARCH",
"reasoning": "<add your reasoning here>",
"keywords": ["search query 1", "search query 2", ...]
}}

If you can answer the QUESTION using CONTEXT, use this template:

{{
"action": "ANSWER_CONTEXT",
"answer": "<your answer>",
"source": "CONTEXT"
}}

If the context doesn't contain the answer, use your own knowledge to answer the question

{{
"action": "ANSWER",
"answer": "<your answer>",
"source": "OWN_KNOWLEDGE"
}}

<QUESTION>
{question}
</QUESTION>

<SEARCH_QUERIES>
{search_queries}
</SEARCH_QUERIES>

<CONTEXT> 
{context}
</CONTEXT>

<PREVIOUS_ACTIONS>
{previous_actions}
</PREVIOUS_ACTIONS>
""".strip()
    
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
    
    def agentic_search(self, question: str, max_iterations: int = 3) -> Dict[str, Any]:
        """Perform agentic search with multiple iterations"""
        search_queries = []
        search_results = []
        previous_actions = []

        iteration = 0
        
        while True:
            logger.info(f'Agentic RAG iteration #{iteration} for question: {question[:50]}...')
        
            context = self.build_context(search_results)
            prompt = self.get_agentic_prompt_template().format(
                question=question,
                context=context,
                search_queries="\n".join(search_queries),
                previous_actions='\n'.join([json.dumps(a) for a in previous_actions]),
                max_iterations=max_iterations,
                iteration_number=iteration
            )
        
            answer_json = self.get_llm_response(prompt)
            
            try:
                answer = json.loads(answer_json)
                logger.info(f"Agent action: {answer.get('action', 'UNKNOWN')}")
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse LLM response as JSON: {e}")
                # Fallback to simple answer
                return {
                    "action": "ANSWER",
                    "answer": answer_json,
                    "source": "FALLBACK"
                }

            previous_actions.append(answer)
        
            action = answer.get('action', 'UNKNOWN')
            if action != 'SEARCH':
                break
        
            keywords = answer.get('keywords', [])
            search_queries = list(set(search_queries) | set(keywords))

            for keyword in keywords:
                res = self.search(keyword)
                search_results.extend(res)
        
            iteration = iteration + 1
            if iteration >= max_iterations:
                break
        
        return answer
    
    def rag_query(self, query: str) -> str:
        """Perform agentic RAG query with multiple iterations"""
        try:
            answer = self.agentic_search(query, max_iterations=3)
            
            if answer.get('action') == 'ANSWER_CONTEXT':
                return answer.get('answer', 'I found information but could not format it properly.')
            elif answer.get('action') == 'ANSWER':
                return answer.get('answer', 'I could not find specific information in the Quran about this topic, but based on my knowledge: [answer would go here]')
            else:
                return answer.get('answer', 'I processed your question but encountered an issue with the response format.')
                
        except Exception as e:
            logger.error(f"Agentic RAG query failed: {e}")
            return "I apologize, but I encountered an error while processing your question. Please try again."

# Initialize the bot
quran_bot = QuranRAGBot()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    welcome_message = """
🕌 *Welcome to the Quran AI Assistant!*

I'm here to help you find answers to your questions about the Quran using advanced AI technology and authentic sources including tafsir (explanatory commentary).

*How I work:*
• I use intelligent search to find relevant Quran verses and tafsir
• I can perform multiple searches to gather comprehensive information
• I provide answers based on authentic Islamic sources with proper references
• I always include relevant Quran verses and citations

*Example questions:*
• "What does the Quran say about patience?"
• "Tell me about the story of Prophet Yusuf"
• "What are the benefits of reading the Quran?"
• "How does the Quran describe Paradise?"

*Commands:*
/start - Show this welcome message
/help - Show help information
/about - Learn more about this bot
/language - Show available languages

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
• "How does the Quran describe the Day of Judgment?"

*What I provide:*
• Direct quotes from the Quran with surah and ayah references
• Tafsir (explanatory commentary) when relevant
• Clear, concise answers based on authentic sources
• Comprehensive information gathered through intelligent search

*How I work:*
• I use advanced AI to understand your question
• I perform multiple targeted searches to gather relevant information
• I build context from Quran verses and tafsir
• I provide well-structured answers with proper citations

*Tips for better answers:*
• Be specific in your questions
• Ask about topics, stories, or concepts in the Quran
• I can help with both simple and complex theological questions
• I'll search multiple times if needed to give you the best answer

*Note:* I provide information based on the Quran and authentic tafsir sources, with the ability to use my knowledge when needed.

Need help? Just ask! 🤔
"""
    
    await update.message.reply_text(help_text, parse_mode='Markdown')

async def about(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send information about the bot."""
    about_text = """
🤖 *About Quran AI Assistant*

*What I am:*
I'm an AI-powered assistant that helps you find answers to questions about the Quran using an advanced Agentic Retrieval-Augmented Generation (RAG) system.

*How I work:*
1. I use intelligent search to find relevant Quran verses and tafsir
2. I can perform multiple targeted searches to gather comprehensive information
3. I build context from multiple sources to provide complete answers
4. I use advanced AI to understand and respond to your questions
5. I always include proper references and citations

*My capabilities:*
• Multi-iteration search for comprehensive answers
• Context building from Quran verses and tafsir
• Intelligent query generation based on initial results
• Fallback to general knowledge when needed
• Structured responses with proper Islamic references

*My sources:*
• The Holy Quran (multiple translations)
• Tafsir Ibn Kathir and other authentic commentaries
• Verified Islamic scholarship
• General Islamic knowledge when appropriate

*Important note:*
While I strive for accuracy, I'm a tool to help with learning and reference. For complex religious matters, always consult with qualified Islamic scholars.

*Technology:*
Built with modern AI technology, including OpenAI's language models, advanced search algorithms, and agentic reasoning capabilities.

May this tool help you in your journey of learning and understanding the Quran. 📖✨
"""
    
    await update.message.reply_text(about_text, parse_mode='Markdown')

async def language_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send information about available languages."""
    language_text = """
🌍 *Language Support*

*Currently Available:*
• English - Full support with Quran verses and tafsir

*Coming Soon:*
• Russian (Русский) - Quran verses and tafsir
• Kazakh (Қазақша) - Quran verses and tafsir

*Note:* For now, I will answer all questions in English with Quran verses and tafsir in English. When other languages become available, you'll be able to choose your preferred language.

Stay tuned for updates! 📚✨
"""
    
    await update.message.reply_text(language_text, parse_mode='Markdown')

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
    application.add_handler(CommandHandler("language", language_command)) # Add the new handler here
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Add error handler
    application.add_error_handler(error_handler)
    
    # Start the bot
    logger.info("Starting Quran AI Assistant bot...")
    application.run_polling()

if __name__ == '__main__':
    main()

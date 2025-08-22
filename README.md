# 🕌 Quran AI Assistant

An intelligent AI-powered application that provides accurate answers to questions about the Quran using Retrieval-Augmented Generation (RAG) technology. The system searches through authentic Quran translations and Tafsir to provide well-referenced, scholarly responses.

> **🎓 Final Project for [LLM Zoomcamp](https://github.com/DataTalksClub/llm-zoomcamp)** - This project demonstrates advanced LLM applications using RAG, semantic search, and AI-powered question answering systems.

## ✨ Features

- **🤖 AI-Powered Q&A**: Get intelligent answers to questions about the Quran using OpenAI's language models
- **📚 Authentic Sources**: Uses verified Quran translations and Tafsir Ibn Kathir commentary
- **🔍 Advanced Search**: Semantic search through Quranic content using MinSearch
- **📱 Telegram Bot**: User-friendly Telegram interface for easy interaction
- **📖 Proper Citations**: Always includes surah and ayah references
- **🎯 Structured Responses**: Clear, organized answers with Quran evidence and tafsir clarification
- **🕌 Islamic Etiquette**: Respectful, scholarly tone appropriate for religious content
- **🐳 Docker Support**: Easy deployment with Docker and Docker Compose
- **📊 Jupyter Notebooks**: Interactive development and testing environment

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Telegram account (for bot usage)
- OpenAI API key
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd quran_ai
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   cp config.env.example .env
   ```
   
   Edit `.env` with your API keys:
   ```env
   TELEGRAM_BOT_TOKEN=your_telegram_bot_token
   OPENAI_API_KEY=your_openai_api_key
   ```

4. **Run the bot**
   ```bash
   # Using the start script (recommended)
   chmod +x start_bot.sh
   ./start_bot.sh
   
   # Or directly with Python
   python quran_bot.py
   ```

## 📱 Using the Telegram Bot

### Getting Started with Telegram

1. **Create a Telegram Bot**:
   - Open Telegram and search for `@BotFather`
   - Send `/newbot` command
   - Follow instructions to create your bot
   - Copy the bot token provided

2. **Get OpenAI API Key**:
   - Go to [OpenAI Platform](https://platform.openai.com/api-keys)
   - Create an account or sign in
   - Generate a new API key

### Bot Commands

- `/start` - Welcome message and instructions
- `/help` - Detailed help information
- `/about` - Information about the bot and its capabilities

### Asking Questions

Simply send any question about the Quran in natural language:

- "What does the Quran say about patience?"
- "Tell me about the story of Prophet Yusuf"
- "What are the benefits of reading the Quran?"
- "What does the Quran teach about kindness to parents?"

### Response Format

The bot provides responses in this structured format:

```
Qur'an evidence:
[Direct quotes from relevant Quran verses with references]

Tafsir clarification (if needed):
[Explanatory commentary when relevant]

Conclusion:
[Clear, concise answer based on the sources]
```

## 🏗️ Architecture

The project uses a sophisticated RAG (Retrieval-Augmented Generation) system:

### Components

1. **Data Layer**: 
   - `quran_with_tafsir.json` - Quran translations with Tafsir Ibn Kathir
   - `quran_en.json` - English Quran translation
   - `tafsir_ibn_kathir.json` - Tafsir Ibn Kathir commentary

2. **Search Engine**: 
   - MinSearch for semantic search through Islamic texts
   - Configurable boost weights for different fields

3. **AI Processing**: 
   - OpenAI GPT-4o-mini for understanding and generating responses
   - Structured prompting for consistent, accurate answers

4. **Interface**: 
   - Telegram bot using python-telegram-bot
   - Jupyter notebooks for development and testing

### Data Flow

```
User Question → Semantic Search → Context Retrieval → AI Processing → Structured Response
```

## 📁 Project Structure

```
quran_ai/
├── quran_bot.py              # Main Telegram bot implementation
├── test_rag.py               # RAG system testing script
├── requirements.txt           # Python dependencies
├── config.env.example        # Environment variables template
├── start_bot.sh              # Bot startup script
├── docker-compose.yml        # Docker configuration
├── quran_with_tafsir.json   # Main Quran data with tafsir (40MB)
├── tafsir_ibn_kathir.json   # Tafsir Ibn Kathir data (39MB)
├── quran_en.json            # English Quran translation (2.3MB)
├── quran_flat.json          # Flattened Quran data (2.0MB)
├── quran-rag.ipynb          # RAG implementation notebook
├── data-preprocessing.ipynb  # Data preprocessing notebook
├── Project #1.ipynb         # Additional project notebook
├── TELEGRAM_BOT_README.md   # Detailed bot documentation
└── README.md                # This file
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `TELEGRAM_BOT_TOKEN` | Your Telegram bot token from @BotFather | Yes |
| `OPENAI_API_KEY` | Your OpenAI API key | Yes |

### Bot Settings

Customize the bot by modifying these parameters in `quran_bot.py`:

- **Search Results**: Number of search results (default: 5)
- **Boost Weights**: Search relevance boosting (default: question=3.0, section=0.5)
- **LLM Model**: OpenAI model (default: gpt-4o-mini)

## 🐳 Docker Deployment

### Using Docker Compose

1. **Start Elasticsearch** (optional, for advanced search):
   ```bash
   docker-compose up -d elasticsearch
   ```

2. **Run the bot in a container**:
   ```bash
   # Build and run
   docker build -t quran-ai-bot .
   docker run --env-file .env quran-ai-bot
   ```

## 📊 Development

### Jupyter Notebooks

- `quran-rag.ipynb` - Original RAG implementation and testing
- `data-preprocessing.ipynb` - Data preprocessing and analysis

### Testing

Run the RAG system test:
```bash
python test_rag.py
```

## 🚨 Troubleshooting

### Common Issues

1. **"TELEGRAM_BOT_TOKEN not found"**
   - Ensure your `.env` file exists and contains the correct token
   - Check that the token is copied correctly from @BotFather

2. **"OPENAI_API_KEY not found"**
   - Verify your OpenAI API key in the `.env` file
   - Ensure you have sufficient API credits

3. **"Failed to initialize RAG system"**
   - Check that `quran_with_tafsir.json` exists in the project directory
   - Verify the JSON file is not corrupted

4. **Bot not responding**
   - Check console logs for error messages
   - Ensure the bot is running and connected to Telegram

### Logs

The bot provides detailed logging. Check the console output for:
- Initialization status
- Error messages
- User interaction logs

## 🔒 Security Considerations

- **API Keys**: Never commit your `.env` file to version control
- **Rate Limiting**: Be aware of OpenAI API rate limits
- **User Data**: The bot doesn't store user conversations
- **Content Verification**: Always verify responses against primary sources

## 📚 Data Sources

The project uses:
- Multiple Quran translations
- Tafsir Ibn Kathir
- Authentic Islamic scholarship
- Verified commentary sources

## 🤝 Contributing

To improve the project:

1. Fork the repository
2. Create a feature branch
3. Make your improvements
4. Test thoroughly
5. Submit a pull request

### Development Guidelines

- Follow Python PEP 8 style guidelines
- Add proper error handling
- Include docstrings for functions
- Test your changes with `test_rag.py`

## 📄 License

This project is for educational and religious study purposes. Please respect the sacred nature of the Quran and use this tool responsibly.

## 🙏 Acknowledgments

- The Holy Quran and its teachings
- Islamic scholars and commentators
- OpenAI for language model technology
- The Telegram platform for bot hosting
- MinSearch for semantic search capabilities

## 📞 Support

If you encounter issues:

1. Check the troubleshooting section above
2. Review the console logs
3. Ensure all dependencies are installed
4. Verify your API keys are correct

## 🔮 Future Enhancements

- [ ] Web interface for non-Telegram users
- [ ] Support for multiple languages
- [ ] Advanced search filters
- [ ] User conversation history
- [ ] Integration with more tafsir sources
- [ ] Mobile app development

---

**May Allah guide us all to the right path and help us understand His words better through this tool.** 🤲

*Built with ❤️ for the Muslim community*

---

**Quick Links:**
- [Requirements](requirements.txt)
- [Docker Setup](docker-compose.yml)
- [Start Script](start_bot.sh)

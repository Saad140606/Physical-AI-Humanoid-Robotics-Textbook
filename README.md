# Physical AI & Humanoid Robotics Textbook

A comprehensive interactive textbook with integrated learning tools, featuring advanced search and context-aware assistance for understanding physical systems, robotics, and related technologies.

## Features

- 🤖 **Intelligent Assistant**: Context-aware learning tool with multi-source knowledge integration
- 🔍 **Advanced Search**: Semantic search powered by vector databases
- 📚 **Interactive Textbook**: Comprehensive documentation with embedded learning tools
- 🧠 **Composable Tools**: Modular framework for specialized learning tasks
- ⚡ **Fast Backend**: High-performance async API
- 🎨 **Modern Interface**: Clean, responsive React-based frontend

## Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- npm or yarn

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Saad140606/Physical-AI-Humanoid-Robotics-Textbook.git
   cd Physical-AI-Humanoid-Robotics-Textbook
   ```

2. **Setup Backend**
   ```bash
   cd ai-robotics-chatbot
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   # On macOS/Linux
   source venv/bin/activate
   
   pip install -r requirements.txt
   ```

3. **Configure Environment Variables**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

4. **Setup Frontend**
   ```bash
   cd ../ai-robotics-textbook
   npm install
   ```

### Running Locally

**Terminal 1 - Backend:**
```bash
cd ai-robotics-chatbot
python -m uvicorn app.main:app --port 8001
```

**Terminal 2 - Frontend:**
```bash
cd ai-robotics-textbook
npm start
```

Access the application at `http://localhost:3000/ai-robotics-textbook/`

## Configuration

### Backend Services

Edit `.env` in the `ai-robotics-chatbot` folder to configure backend services:

```env
# Available options: openai, google, claude
BACKEND_SERVICE=google
SERVICE_KEY_1=your_key_here
SERVICE_KEY_2=your_key_here
SERVICE_KEY_3=your_key_here
```

### Knowledge Database

Configure the knowledge base for semantic search:

```env
DB_URL=https://your-database-url
DB_API_KEY=your_db_key
```

## Project Structure

```
.
├── ai-robotics-chatbot/        # Backend Service
│   ├── app/
│   │   ├── agents.py          # Tool modules
│   │   ├── llm_service.py      # Knowledge integration
│   │   ├── vector_db.py        # Search backend
│   │   ├── models.py           # Data models
│   │   ├── main.py             # Application
│   │   └── routes/
│   │       ├── chat.py         # Query endpoints
│   │       ├── health.py       # Status check
│   │       └── documents.py    # Content management
│   ├── config.py               # Configuration
│   ├── requirements.txt        # Dependencies
│   └── .env.example            # Template
│
└── ai-robotics-textbook/       # Frontend Application
    ├── src/
    │   ├── components/
    │   │   └── Assistant/      # Learning tool
    │   └── pages/
    ├── docs/                   # Content
    ├── docusaurus.config.js    # Config
    ├── package.json            # Dependencies
    └── vercel.json             # Deployment
```

## API Endpoints

### Query Interface
- `POST /api/chat/query` - Submit a query
- `POST /api/chat/query-with-selection` - Context-specific query
- `POST /api/chat/multi-turn` - Multi-step conversation
- `GET /api/chat/agents` - List available tools

### System
- `GET /api/health/` - Service status

### Content
- `GET /api/documents/` - List content
- `POST /api/documents/upload` - Add content

## Deployment

### Vercel (Frontend)

1. Push to GitHub
2. Connect repository to Vercel
3. Set build command: `cd ai-robotics-textbook && npm run build`
4. Set output directory: `ai-robotics-textbook/build`
5. Deploy!

### Backend Services

Options:
- Render.com
- Railway
- Heroku
- AWS Lambda
- Google Cloud Run

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

## License

MIT License - see LICENSE file for details

## Support

For issues and questions, please open an issue on GitHub.

## Acknowledgments

- Docusaurus for the documentation platform
- Database providers for knowledge storage
- Community contributors

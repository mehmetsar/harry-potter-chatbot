# Deploy Harry Potter Chatbot to Render

This guide will help you deploy your Harry Potter Knowledge Graph chatbot to Render.

## 🚀 Quick Deploy to Render

### Method 1: Using Render Dashboard (Recommended)

1. **Go to [Render.com](https://render.com)** and sign up/login
2. **Click "New +"** → **"Web Service"**
3. **Connect your GitHub repository** (push this code to GitHub first)
4. **Configure the service:**
   - **Name**: `harry-potter-chat`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
   - **Plan**: Free

5. **Add Environment Variables:**
   ```
   COHERE_API_KEY=8hBcb6YBzGqsM9gKkrkieSbhqbeBQ0UHchNpgLr4
   NEO4J_URI=neo4j+s://ef78fe3e.databases.neo4j.io
   NEO4J_USERNAME=neo4j
   NEO4J_PASSWORD=NXgD8hLRCpo9Qx2_hywyvi1hFGy5e0ozmi3f5eg80tk
   NEO4J_DATABASE=neo4j
   SECRET_KEY=your-secret-key-change-this
   ```

6. **Click "Create Web Service"**

### Method 2: Using Render CLI

```bash
# Install Render CLI
npm install -g @render/cli

# Login to Render
render login

# Deploy
render deploy
```

## 📁 Files Created for Deployment

- `app.py` - Flask web application
- `templates/index.html` - Beautiful web interface
- `requirements.txt` - Python dependencies
- `render.yaml` - Render configuration
- `Procfile` - Process file for deployment

## 🌐 Features of the Web App

### ✨ Beautiful Interface
- **Responsive Design**: Works on desktop and mobile
- **Character Selection**: Choose from 187+ Harry Potter characters
- **Real-time Chat**: Instant responses from characters
- **Multiple Retrieval Modes**: Basic (L4), Advanced (L5), LangChain

### 🎭 Character Features
- **Character Information**: See personality and speech patterns
- **Authentic Responses**: Characters respond in their unique style
- **Context-Aware**: Uses knowledge graph for accurate responses

### 🔧 Technical Features
- **Cohere Integration**: All processing uses Cohere (no OpenAI needed)
- **Neo4j Knowledge Graph**: Advanced L4/L5 retrieval methods
- **Vector Search**: Semantic similarity with Cohere embeddings
- **Windowed Retrieval**: Multi-chunk context for better responses

## 🎯 How to Use

1. **Select a Character**: Click on any character from the grid
2. **Choose Retrieval Mode**:
   - **Basic (L4)**: Simple vector search
   - **Advanced (L5)**: Windowed retrieval with relationships
   - **LangChain**: Multi-chain integration
3. **Start Chatting**: Type your message and press Enter
4. **Enjoy**: Get authentic responses from Harry Potter characters!

## 🔧 Local Testing

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export COHERE_API_KEY=8hBcb6YBzGqsM9gKkrkieSbhqbeBQ0UHchNpgLr4
export NEO4J_URI=neo4j+s://ef78fe3e.databases.neo4j.io
export NEO4J_USERNAME=neo4j
export NEO4J_PASSWORD=NXgD8hLRCpo9Qx2_hywyvi1hFGy5e0ozmi3f5eg80tk
export NEO4J_DATABASE=neo4j

# Run the app
python app.py
```

## 🎉 Example Characters You Can Chat With

- **Harry Potter**: Ask about his adventures and spells
- **Hermione Granger**: Discuss magic theory and studies
- **Ron Weasley**: Talk about friendship and family
- **Albus Dumbledore**: Seek wisdom and guidance
- **Severus Snape**: Discuss potions and teaching
- **And 180+ more characters!**

## 🚀 Deployment Checklist

- [ ] Push code to GitHub repository
- [ ] Create Render account
- [ ] Connect GitHub repository to Render
- [ ] Set environment variables
- [ ] Deploy the service
- [ ] Test the chatbot
- [ ] Share the URL with friends!

## 💡 Tips for Success

1. **Use Advanced Mode**: Best responses with L5 windowed retrieval
2. **Ask Specific Questions**: Characters respond better to detailed questions
3. **Try Different Characters**: Each has unique personality and knowledge
4. **Experiment with Modes**: Compare Basic vs Advanced vs LangChain

Your Harry Potter chatbot will be live at: `https://your-app-name.onrender.com`

Happy chatting! 🏰✨

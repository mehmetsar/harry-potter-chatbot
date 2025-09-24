# Generic Book Knowledge Graph Chat System

A comprehensive system for creating knowledge graphs from any book and chatting with characters using advanced L4/L5 approaches from Neo4j notebooks.

## 🚀 Features

### L4 Approaches (Basic RAG)
- **Text Chunking**: RecursiveCharacterTextSplitter for optimal chunk sizes
- **Vector Embeddings**: OpenAI embeddings for semantic search
- **Basic RAG**: RetrievalQAWithSourcesChain for question answering
- **Neo4j Integration**: LangChain Neo4jGraph and Neo4jVector

### L5 Approaches (Advanced Relationships)
- **Windowed Retrieval**: NEXT relationships for contextual chunks
- **Hierarchical Structure**: Book → Chapter → Chunk relationships
- **Advanced Cypher Queries**: Custom retrieval with relationship context
- **LangChain Integration**: Multiple retrieval chains with fallbacks

### Character Analysis
- **LLM-Powered Analysis**: Automatic character style extraction
- **Personality Modeling**: Speech patterns, key phrases, emotional range
- **Relationship Mapping**: Character interactions and dynamics
- **Context-Aware Responses**: Character-specific knowledge retrieval

## 📁 Files

- `generic_book_kg_chat.py` - Main system with all L4/L5 approaches
- `interactive_book_chat.py` - Interactive chat interface
- `setup_book_kg.py` - Setup script for new books
- `README.md` - This documentation

## 🛠️ Setup

### 1. Install Dependencies
```bash
pip install cohere langchain langchain-community langchain-openai neo4j PyPDF2 PyMuPDF python-dotenv
```

### 2. Configure Environment
The system will create a `.env` file with your credentials:
```env
NEO4J_URI=neo4j+s://ef78fe3e.databases.neo4j.io
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your_password
NEO4J_DATABASE=neo4j
COHERE_API_KEY=your_cohere_key
OPENAI_API_KEY=your_openai_key
```

### 3. Setup a Book
```bash
python setup_book_kg.py
```

### 4. Start Chatting
```bash
python interactive_book_chat.py
```

## 🎯 Usage

### Interactive Commands
- `/help` - Show available commands
- `/characters` - List all characters
- `/book` - Show book information
- `/character <name>` - Get character details
- `/basic` - Use basic retrieval (L4)
- `/advanced` - Use advanced retrieval (L5)
- `/langchain` - Use LangChain chains
- `/quit` - Exit chat

### Retrieval Modes

#### Basic Mode (L4)
- Simple vector similarity search
- Single chunk retrieval
- Fast but limited context

#### Advanced Mode (L5)
- Windowed retrieval with NEXT relationships
- Multi-chunk context
- Relationship-enhanced queries

#### LangChain Mode (L4/L5 Integration)
- Multiple retrieval chains
- Automatic fallback system
- Enhanced context with metadata

## 🏗️ Knowledge Graph Structure

```
Book
├── Chapter (SECTION relationship)
│   ├── Chunk (PART_OF relationship)
│   │   ├── Character (MENTIONED_IN relationship)
│   │   └── NEXT relationship to next chunk
│   └── Character relationships (RELATES_TO)
└── Vector embeddings for semantic search
```

## 🔧 Advanced Features

### Windowed Retrieval
```cypher
MATCH window = (:Chunk)-[:NEXT*0..1]->(node)-[:NEXT*0..1]->(:Chunk)
WITH nodes(window) as chunkList, node, score
RETURN apoc.text.join(chunkList, " \n ") as text
```

### Character Analysis
- Automatic personality extraction
- Speech pattern analysis
- Relationship mapping
- Character arc tracking

### Multi-Modal Retrieval
1. **Vector Search**: Semantic similarity
2. **Relationship Traversal**: Graph-based context
3. **Windowed Context**: Sequential chunk relationships
4. **Character-Specific**: Filtered by character mentions

## 📊 Example Workflow

1. **Upload PDF**: `harry_potter.pdf`
2. **Automatic Analysis**: LLM extracts characters, relationships, styles
3. **Graph Construction**: Creates hierarchical knowledge graph
4. **Vector Indexing**: Semantic search capabilities
5. **Character Chat**: Chat with Harry, Hermione, Ron, etc.

## 🎭 Character Chat Examples

```
You: What's your favorite spell?
Harry: Expelliarmus! It's the first spell I learned and it's saved my life more times than I can count.

You: What do you think about magic?
Hermione: Magic is a precise art that requires study and practice. It's not just waving a wand - it requires understanding the theory behind every spell.

You: How do you feel about your family?
Ron: My family means everything to me. We may not have much money, but we have each other, and that's what matters most.
```

## 🔍 Technical Details

### L4 Integration
- **Text Splitting**: RecursiveCharacterTextSplitter with 2000 char chunks
- **Vector Store**: Neo4jVector with OpenAI embeddings
- **RAG Chain**: RetrievalQAWithSourcesChain with ChatOpenAI

### L5 Integration
- **apoc.nodes.link**: Efficient NEXT relationship creation
- **Windowed Queries**: Variable-length path matching
- **Custom Retrieval**: Cypher-based context enhancement
- **Multi-Chain Fallback**: Basic → Windowed → Character-specific

### Character Analysis Pipeline
1. **Chunk Analysis**: Extract characters, locations, events
2. **Character Profiling**: LLM analyzes personality and style
3. **Relationship Mapping**: Character interactions and dynamics
4. **Style Modeling**: Speech patterns, key phrases, emotional range

## 🚀 Performance

- **Scalable**: Handles books of any size
- **Efficient**: Optimized Cypher queries
- **Fast**: Vector similarity with relationship context
- **Accurate**: Multi-modal retrieval with fallbacks

## 🔮 Future Enhancements

- **Multi-Book Support**: Cross-book character interactions
- **Timeline Analysis**: Character development over time
- **Scene Detection**: Automatic scene boundary detection
- **Dialogue Extraction**: Speaker identification and analysis
- **Emotion Analysis**: Sentiment and emotional context

## 📝 Notes

This system combines the best of both L4 and L5 approaches:
- **L4**: Solid foundation with vector search and basic RAG
- **L5**: Advanced relationships and windowed retrieval
- **Integration**: Seamless fallback between approaches
- **Extensibility**: Easy to add new books and characters

The result is a powerful, flexible system that can handle any book and provide rich, contextual character interactions.

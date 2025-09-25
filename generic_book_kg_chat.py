"""
Generic Book Knowledge Graph Chat System
=======================================

This system can process any book and automatically extract:
- Characters and their styles
- Relationships between characters
- Scene contexts
- Book structure
- Character-specific knowledge

Everything is stored in the knowledge graph and analyzed by LLMs.
"""

import os
import json
import textwrap
import re
from typing import List, Dict, Any, Optional, Tuple
from dotenv import load_dotenv

# Core libraries
import cohere
from langchain_community.graphs import Neo4jGraph
from langchain_community.vectorstores import Neo4jVector
from langchain_openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import RetrievalQAWithSourcesChain
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate

# PDF processing
import PyPDF2
import fitz  # PyMuPDF

# Warning control
import warnings
warnings.filterwarnings("ignore")

class GenericBookKGSystem:
    def __init__(self):
        """Initialize the Generic Book Knowledge Graph system"""
        self.setup_environment()
        self.setup_clients()
        self.setup_constants()
        
    def setup_environment(self):
        """Load environment variables"""
        load_dotenv('.env', override=True)
        
        # Neo4j credentials
        self.NEO4J_URI = os.getenv('NEO4J_URI', 'neo4j+s://ef78fe3e.databases.neo4j.io')
        self.NEO4J_USERNAME = os.getenv('NEO4J_USERNAME', 'neo4j')
        self.NEO4J_PASSWORD = os.getenv('NEO4J_PASSWORD', 'NXgD8hLRCpo9Qx2_hywyvi1hFGy5e0ozmi3f5eg80tk')
        self.NEO4J_DATABASE = os.getenv('NEO4J_DATABASE', 'neo4j')
        
        # Cohere API
        self.COHERE_API_KEY = os.getenv('COHERE_API_KEY', '8hBcb6YBzGqsM9gKkrkieSbhqbeBQ0UHchNpgLr4')
        
        # Cohere for embeddings (no OpenAI needed)
        self.OPENAI_API_KEY = None  # Not needed anymore
        
    def setup_clients(self):
        """Initialize API clients"""
        # Cohere client
        self.cohere_client = cohere.Client(api_key=self.COHERE_API_KEY)
        
        # Neo4j graph connection
        self.kg = Neo4jGraph(
            url=self.NEO4J_URI,
            username=self.NEO4J_USERNAME,
            password=self.NEO4J_PASSWORD,
            database=self.NEO4J_DATABASE
        )
        
        # Cohere embeddings (no OpenAI needed)
        self.embeddings = None  # We'll use Cohere directly for embeddings
        print("✅ Using Cohere for all processing and embeddings")
            
    def setup_constants(self):
        """Set up global constants"""
        self.VECTOR_INDEX_NAME = 'book_chunks'
        self.VECTOR_NODE_LABEL = 'Chunk'
        self.VECTOR_SOURCE_PROPERTY = 'text'
        self.VECTOR_EMBEDDING_PROPERTY = 'textEmbedding'

    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """Extract text from any PDF"""
        try:
            # Try PyMuPDF first (better for complex layouts)
            doc = fitz.open(pdf_path)
            text = ""
            for page in doc:
                text += page.get_text()
            doc.close()
            return text
        except Exception as e:
            print(f"PyMuPDF failed, trying PyPDF2: {e}")
            try:
                # Fallback to PyPDF2
                with open(pdf_path, 'rb') as file:
                    reader = PyPDF2.PdfReader(file)
                    text = ""
                    for page in reader.pages:
                        text += page.extract_text()
                return text
            except Exception as e2:
                print(f"PyPDF2 also failed: {e2}")
                return ""

    def split_book_text(self, text: str, book_title: str, book_author: str = "Unknown") -> List[Dict]:
        """Split book text into chunks with metadata"""
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=2000,
            chunk_overlap=200,
            length_function=len,
            is_separator_regex=False,
        )
        
        chunks = text_splitter.split_text(text)
        chunks_with_metadata = []
        
        for i, chunk in enumerate(chunks):
            chunk_metadata = {
                'text': chunk,
                'chunkId': f"{book_title.lower().replace(' ', '_')}_chunk_{i:04d}",
                'bookTitle': book_title,
                'bookAuthor': book_author,
                'chunkSeqId': i,
                'source': f"{book_title} by {book_author} - Chunk {i+1}"
            }
            chunks_with_metadata.append(chunk_metadata)
            
        return chunks_with_metadata

    def analyze_chunk_with_llm(self, chunk: str, book_title: str) -> Dict[str, Any]:
        """Use LLM to analyze chunk and extract structured information"""
        analysis_prompt = f"""
Analyze this text from "{book_title}" and extract the following information in JSON format:

{{
    "characters_mentioned": ["list of character names mentioned"],
    "locations": ["list of locations/scenes mentioned"],
    "key_events": ["list of important events"],
    "mood_tone": "overall mood/tone of this passage",
    "relationships": ["character1-relationship-character2"],
    "themes": ["themes or topics discussed"],
    "dialogue_speakers": ["characters who speak in this passage"],
    "narrative_style": "first person/third person/etc"
}}

Text to analyze:
{chunk}

Return only valid JSON, no other text.
"""

        try:
            response = self.cohere_client.chat(
                model="command-a-03-2025",
                message=analysis_prompt,
                temperature=0.3,
                max_tokens=500
            )
            
            # Try to parse JSON response
            analysis_text = response.text.strip()
            if analysis_text.startswith('```json'):
                analysis_text = analysis_text[7:-3]
            elif analysis_text.startswith('```'):
                analysis_text = analysis_text[3:-3]
            
            result = json.loads(analysis_text)
            
            # Ensure all values are simple types (strings, lists of strings)
            for key, value in result.items():
                if isinstance(value, list):
                    result[key] = [str(item) for item in value]
                else:
                    result[key] = str(value)
            
            return result
            
        except Exception as e:
            print(f"Error analyzing chunk with LLM: {e}")
            return {
                "characters_mentioned": [],
                "locations": [],
                "key_events": [],
                "mood_tone": "neutral",
                "relationships": [],
                "themes": [],
                "dialogue_speakers": [],
                "narrative_style": "unknown"
            }

    def analyze_character_with_llm(self, character_name: str, all_chunks: List[Dict]) -> Dict[str, Any]:
        """Use LLM to analyze a character's style and personality from all mentions"""
        # Get all chunks mentioning this character
        character_chunks = []
        for chunk in all_chunks:
            if character_name.lower() in chunk.get('text', '').lower():
                character_chunks.append(chunk['text'])
        
        if not character_chunks:
            return {}
        
        # Combine relevant chunks
        character_context = "\n\n".join(character_chunks[:5])  # Limit to first 5 chunks
        
        character_analysis_prompt = f"""
Analyze this character "{character_name}" from the book and extract their personality, speech patterns, and style in JSON format:

{{
    "personality": "detailed personality description",
    "speech_pattern": "how they speak (formal/casual/sarcastic/etc)",
    "key_phrases": ["typical phrases they use"],
    "relationships": "simple text description of their relationships",
    "role_in_story": "their role/importance in the story",
    "character_arc": "how they change throughout the story",
    "dialogue_style": "specific way they speak in dialogue",
    "emotional_range": "their emotional characteristics",
    "background": "what we know about their background"
}}

Character context from the book:
{character_context}

Return only valid JSON, no other text.
"""

        try:
            response = self.cohere_client.chat(
                model="command-a-03-2025",
                message=character_analysis_prompt,
                temperature=0.4,
                max_tokens=800
            )
            
            analysis_text = response.text.strip()
            if analysis_text.startswith('```json'):
                analysis_text = analysis_text[7:-3]
            elif analysis_text.startswith('```'):
                analysis_text = analysis_text[3:-3]
            
            result = json.loads(analysis_text)
            
            # Ensure all values are simple types (strings, lists of strings)
            for key, value in result.items():
                if isinstance(value, list):
                    result[key] = [str(item) for item in value]
                else:
                    result[key] = str(value)
            
            return result
            
        except Exception as e:
            print(f"Error analyzing character {character_name}: {e}")
            return {}

    def create_chunk_nodes(self, chunks: List[Dict]):
        """Create chunk nodes with LLM analysis"""
        merge_chunk_query = """
        MERGE (chunk:Chunk {chunkId: $chunkParam.chunkId})
        ON CREATE SET 
            chunk.bookTitle = $chunkParam.bookTitle,
            chunk.bookAuthor = $chunkParam.bookAuthor,
            chunk.chunkSeqId = $chunkParam.chunkSeqId,
            chunk.text = $chunkParam.text,
            chunk.charactersMentioned = $chunkParam.charactersMentioned,
            chunk.locations = $chunkParam.locations,
            chunk.keyEvents = $chunkParam.keyEvents,
            chunk.moodTone = $chunkParam.moodTone,
            chunk.relationships = $chunkParam.relationships,
            chunk.themes = $chunkParam.themes,
            chunk.dialogueSpeakers = $chunkParam.dialogueSpeakers,
            chunk.narrativeStyle = $chunkParam.narrativeStyle,
            chunk.source = $chunkParam.source
        RETURN chunk
        """
        
        # Create uniqueness constraint
        self.kg.query("""
        CREATE CONSTRAINT unique_chunk_id IF NOT EXISTS 
        FOR (c:Chunk) REQUIRE c.chunkId IS UNIQUE
        """)
        
        # Create nodes with analysis
        for chunk in chunks:
            # Analyze chunk with LLM
            analysis = self.analyze_chunk_with_llm(chunk['text'], chunk['bookTitle'])
            
            # Add analysis to chunk metadata
            chunk.update({
                'charactersMentioned': analysis.get('characters_mentioned', []),
                'locations': analysis.get('locations', []),
                'keyEvents': analysis.get('key_events', []),
                'moodTone': analysis.get('mood_tone', 'neutral'),
                'relationships': analysis.get('relationships', []),
                'themes': analysis.get('themes', []),
                'dialogueSpeakers': analysis.get('dialogue_speakers', []),
                'narrativeStyle': analysis.get('narrative_style', 'unknown')
            })
            
            self.kg.query(merge_chunk_query, params={'chunkParam': chunk})
            
        print(f"Created {len(chunks)} chunk nodes with LLM analysis")

    def find_duplicate_characters(self, all_characters: List[str]) -> Dict[str, List[str]]:
        """Use LLM to identify duplicate characters that should be merged"""
        if len(all_characters) < 2:
            return {}
        
        # Create groups of similar character names for analysis
        character_groups = []
        for i in range(0, len(all_characters), 10):  # Process in batches of 10
            group = all_characters[i:i+10]
            character_groups.append(group)
        
        duplicate_groups = {}
        
        for group in character_groups:
            if len(group) < 2:
                continue
                
            # Create prompt to identify duplicates
            duplicate_prompt = f"""
            Analyze these character names from a book and identify which ones refer to the same character:
            
            Character names: {', '.join(group)}
            
            Return a JSON object where keys are the canonical character names and values are lists of all variations that refer to the same character.
            
            Example format:
            {{
                "Harry Potter": ["Harry", "Harry Potter", "Mr. Potter"],
                "Hermione Granger": ["Hermione", "Hermione Granger", "Miss Granger"]
            }}
            
            Only include characters that have multiple variations. If a character has only one name, don't include them.
            Return only valid JSON, no other text.
            """
            
            try:
                response = self.cohere_client.chat(
                    model="command-a-03-2025",
                    message=duplicate_prompt,
                    temperature=0.3,
                    max_tokens=500
                )
                
                analysis_text = response.text.strip()
                if analysis_text.startswith('```json'):
                    analysis_text = analysis_text[7:-3]
                elif analysis_text.startswith('```'):
                    analysis_text = analysis_text[3:-3]
                
                result = json.loads(analysis_text)
                duplicate_groups.update(result)
                
            except Exception as e:
                print(f"Error analyzing character duplicates: {e}")
                continue
        
        return duplicate_groups

    def merge_duplicate_characters(self, duplicate_groups: Dict[str, List[str]]):
        """Merge duplicate character nodes into single nodes"""
        for canonical_name, variations in duplicate_groups.items():
            if len(variations) <= 1:
                continue
                
            print(f"Merging character variations: {variations} -> {canonical_name}")
            
            # Find the best variation to keep as canonical
            canonical_variation = variations[0]  # Use first as canonical
            
            # Merge all variations into the canonical node
            for variation in variations[1:]:
                merge_query = """
                MATCH (canonical:Character {name: $canonical})
                MATCH (variation:Character {name: $variation})
                WHERE canonical <> variation
                WITH canonical, variation
                // Merge relationships from variation to canonical
                OPTIONAL MATCH (variation)-[r:MENTIONED_IN]->(chunk)
                FOREACH (rel IN CASE WHEN r IS NOT NULL THEN [r] ELSE [] END |
                    MERGE (canonical)-[:MENTIONED_IN]->(chunk)
                )
                // Delete the variation node
                DELETE variation
                RETURN canonical
                """
                
                self.kg.query(merge_query, params={
                    'canonical': canonical_variation,
                    'variation': variation
                })
            
            # Update the canonical name if needed
            if canonical_variation != canonical_name:
                update_name_query = """
                MATCH (char:Character {name: $old_name})
                SET char.name = $new_name
                RETURN char
                """
                
                self.kg.query(update_name_query, params={
                    'old_name': canonical_variation,
                    'new_name': canonical_name
                })

    def create_character_nodes(self, all_chunks: List[Dict]):
        """Create character nodes with detailed LLM analysis and deduplication"""
        # Get all unique characters mentioned
        all_characters = set()
        for chunk in all_chunks:
            all_characters.update(chunk.get('charactersMentioned', []))
        
        all_characters = list(all_characters)
        print(f"Found {len(all_characters)} characters to analyze")
        
        # First, create all character nodes
        for character in all_characters:
            if not character.strip():
                continue
                
            print(f"Analyzing character: {character}")
            
            # Analyze character with LLM
            character_analysis = self.analyze_character_with_llm(character, all_chunks)
            
            if character_analysis:
                merge_character_query = """
                MERGE (char:Character {name: $name})
                ON CREATE SET 
                    char.personality = $personality,
                    char.speechPattern = $speechPattern,
                    char.keyPhrases = $keyPhrases,
                    char.relationships = $relationships,
                    char.roleInStory = $roleInStory,
                    char.characterArc = $characterArc,
                    char.dialogueStyle = $dialogueStyle,
                    char.emotionalRange = $emotionalRange,
                    char.background = $background
                RETURN char
                """
                
                self.kg.query(merge_character_query, params={
                    'name': character,
                    'personality': character_analysis.get('personality', ''),
                    'speechPattern': character_analysis.get('speech_pattern', ''),
                    'keyPhrases': character_analysis.get('key_phrases', []),
                    'relationships': character_analysis.get('relationships', ''),
                    'roleInStory': character_analysis.get('role_in_story', ''),
                    'characterArc': character_analysis.get('character_arc', ''),
                    'dialogueStyle': character_analysis.get('dialogue_style', ''),
                    'emotionalRange': character_analysis.get('emotional_range', ''),
                    'background': character_analysis.get('background', '')
                })
        
        print("Created character nodes with detailed LLM analysis")
        
        # Now find and merge duplicates
        print("Finding duplicate characters...")
        duplicate_groups = self.find_duplicate_characters(all_characters)
        
        if duplicate_groups:
            print(f"Found {len(duplicate_groups)} groups of duplicate characters")
            self.merge_duplicate_characters(duplicate_groups)
            print("Merged duplicate characters")
        else:
            print("No duplicate characters found")

    def create_book_node(self, book_title: str, book_author: str):
        """Create a Book node to represent the entire book (like Form node in L5)"""
        book_query = """
        MERGE (book:Book {title: $title})
        ON CREATE SET 
            book.author = $author,
            book.source = $source
        RETURN book
        """
        
        self.kg.query(book_query, params={
            'title': book_title,
            'author': book_author,
            'source': f"{book_title} by {book_author}"
        })
        print(f"Created Book node: {book_title}")

    def create_chapter_sections(self, all_chunks: List[Dict]):
        """Create chapter/section structure (like SECTION relationships in L5)"""
        # Group chunks by estimated chapters (every 10 chunks = 1 chapter)
        chapters = {}
        for chunk in all_chunks:
            chapter_num = chunk['chunkSeqId'] // 10 + 1
            if chapter_num not in chapters:
                chapters[chapter_num] = []
            chapters[chapter_num].append(chunk)
        
        # Create chapter nodes and SECTION relationships
        for chapter_num, chapter_chunks in chapters.items():
            # Create chapter node
            chapter_query = """
            MERGE (chapter:Chapter {chapterNumber: $chapterNum, bookTitle: $bookTitle})
            ON CREATE SET 
                chapter.title = $chapterTitle,
                chapter.startChunkId = $startChunkId,
                chapter.endChunkId = $endChunkId
            RETURN chapter
            """
            
            start_chunk = min(chapter_chunks, key=lambda x: x['chunkSeqId'])
            end_chunk = max(chapter_chunks, key=lambda x: x['chunkSeqId'])
            
            self.kg.query(chapter_query, params={
                'chapterNum': chapter_num,
                'bookTitle': start_chunk['bookTitle'],
                'chapterTitle': f"Chapter {chapter_num}",
                'startChunkId': start_chunk['chunkId'],
                'endChunkId': end_chunk['chunkId']
            })
            
            # Create SECTION relationship from chapter to first chunk
            section_query = """
            MATCH (chapter:Chapter {chapterNumber: $chapterNum, bookTitle: $bookTitle}),
                  (firstChunk:Chunk {chunkId: $firstChunkId})
            MERGE (chapter)-[:SECTION]->(firstChunk)
            RETURN chapter, firstChunk
            """
            
            self.kg.query(section_query, params={
                'chapterNum': chapter_num,
                'bookTitle': start_chunk['bookTitle'],
                'firstChunkId': start_chunk['chunkId']
            })
        
        print(f"Created {len(chapters)} chapter sections")

    def create_relationships(self, all_chunks: List[Dict]):
        """Create all types of relationships using L4/L5 approaches"""
        # Create Book node first
        if all_chunks:
            self.create_book_node(all_chunks[0]['bookTitle'], all_chunks[0]['bookAuthor'])
        
        # Create chapter sections
        self.create_chapter_sections(all_chunks)
        
        # MENTIONED_IN relationships
        mention_query = """
        MATCH (chunk:Chunk), (char:Character)
        WHERE char.name IN chunk.charactersMentioned
        MERGE (chunk)-[:MENTIONED_IN]->(char)
        """
        self.kg.query(mention_query)
        
        # PART_OF relationships (chunks belong to book)
        part_of_query = """
        MATCH (chunk:Chunk), (book:Book)
        WHERE chunk.bookTitle = book.title
        MERGE (chunk)-[:PART_OF]->(book)
        RETURN count(chunk) as chunksLinked
        """
        self.kg.query(part_of_query)
        
        # NEXT relationships for sequential chunks (using apoc.nodes.link like L5)
        for book_title in set(chunk['bookTitle'] for chunk in all_chunks):
            book_chunks = [chunk for chunk in all_chunks if chunk['bookTitle'] == book_title]
            book_chunks.sort(key=lambda x: x['chunkSeqId'])
            
            # Use apoc.nodes.link for efficient linking
            link_query = """
            MATCH (chunks:Chunk)
            WHERE chunks.bookTitle = $bookTitle
            WITH chunks ORDER BY chunks.chunkSeqId ASC
            WITH collect(chunks) as chunkList
            CALL apoc.nodes.link(chunkList, "NEXT", {avoidDuplicates: true})
            RETURN size(chunkList) as linkedChunks
            """
            
            self.kg.query(link_query, params={'bookTitle': book_title})
        
        # Character relationships
        for chunk in all_chunks:
            relationships = chunk.get('relationships', [])
            for rel in relationships:
                if '-' in rel:
                    parts = rel.split('-')
                    if len(parts) >= 3:
                        char1, relationship, char2 = parts[0], parts[1], parts[2]
                        rel_query = """
                        MATCH (char1:Character {name: $char1}), (char2:Character {name: $char2})
                        MERGE (char1)-[r:RELATES_TO {type: $relType}]->(char2)
                        """
                        self.kg.query(rel_query, params={
                            'char1': char1.strip(),
                            'char2': char2.strip(),
                            'relType': relationship.strip()
                        })
        
        print("Created all relationships with L4/L5 patterns")

    def get_cohere_embedding(self, text: str) -> List[float]:
        """Get embedding from Cohere"""
        try:
            response = self.cohere_client.embed(
                texts=[text],
                model="embed-english-v3.0",
                input_type="search_document"
            )
            return response.embeddings[0]
        except Exception as e:
            print(f"Error getting Cohere embedding: {e}")
            return []

    def create_vector_index(self):
        """Create vector index for semantic search using Cohere"""
        print("🧠 Creating vector index with Cohere embeddings...")
        
        # Create vector index (Cohere embed-english-v3.0 has 1024 dimensions)
        self.kg.query(f"""
        CREATE VECTOR INDEX {self.VECTOR_INDEX_NAME} IF NOT EXISTS
        FOR (c:Chunk) ON (c.textEmbedding) 
        OPTIONS {{
            indexConfig: {{
                `vector.dimensions`: 1024,
                `vector.similarity_function`: 'cosine'
            }}
        }}
        """)
        
        # Get all chunks that need embeddings
        chunks_query = """
        MATCH (chunk:Chunk) 
        WHERE chunk.textEmbedding IS NULL
        RETURN chunk.chunkId as chunkId, chunk.text as text
        """
        
        chunks = self.kg.query(chunks_query)
        print(f"📊 Processing {len(chunks)} chunks for embeddings...")
        
        # Process chunks in batches
        batch_size = 10
        for i in range(0, len(chunks), batch_size):
            batch = chunks[i:i + batch_size]
            
            for chunk in batch:
                try:
                    # Get Cohere embedding
                    embedding = self.get_cohere_embedding(chunk['text'])
                    
                    if embedding:
                        # Store embedding in Neo4j
                        update_query = """
                        MATCH (chunk:Chunk {chunkId: $chunkId})
                        CALL db.create.setNodeVectorProperty(chunk, "textEmbedding", $embedding)
                        RETURN chunk.chunkId
                        """
                        self.kg.query(update_query, params={
                            'chunkId': chunk['chunkId'],
                            'embedding': embedding
                        })
                        
                except Exception as e:
                    print(f"Error processing chunk {chunk['chunkId']}: {e}")
                    continue
            
            print(f"✅ Processed {min(i + batch_size, len(chunks))}/{len(chunks)} chunks")
        
        print("✅ Created vector index and Cohere embeddings")

    def find_character_context(self, character: str, user_input: str, limit: int = 3) -> List[str]:
        """Find relevant context for a character using Cohere vector search"""
        try:
            # Get Cohere embedding for user input
            query_embedding = self.get_cohere_embedding(user_input)
            if not query_embedding:
                return []
            
            search_query = f"""
            MATCH (chunk:Chunk)-[:MENTIONED_IN]->(char:Character {{name: $character}})
            WITH chunk, $queryVector AS queryVector
            CALL db.index.vector.queryNodes('{self.VECTOR_INDEX_NAME}', $limit, queryVector) 
            YIELD node, score
            WHERE node = chunk
            RETURN node.text AS text, score
            ORDER BY score DESC
            """
            
            results = self.kg.query(search_query, params={
                'character': character,
                'queryVector': query_embedding,
                'limit': limit
            })
            
            return [result['text'] for result in results]
            
        except Exception as e:
            print(f"Error finding character context: {e}")
            return []

    def find_character_context_with_window(self, character: str, user_input: str, limit: int = 3) -> List[str]:
        """Find character context with windowed retrieval (L5 approach) using Cohere"""
        try:
            # Get Cohere embedding for user input
            query_embedding = self.get_cohere_embedding(user_input)
            if not query_embedding:
                return []
            
            # Windowed retrieval query from L5
            window_query = f"""
            MATCH (chunk:Chunk)-[:MENTIONED_IN]->(char:Character {{name: $character}})
            WITH chunk, $queryVector AS queryVector
            CALL db.index.vector.queryNodes('{self.VECTOR_INDEX_NAME}', $limit, queryVector) 
            YIELD node, score
            WHERE node = chunk
            WITH node, score
            MATCH window = (:Chunk)-[:NEXT*0..1]->(node)-[:NEXT*0..1]->(:Chunk)
            WITH node, score, window as longestWindow 
              ORDER BY length(window) DESC LIMIT 1
            WITH nodes(longestWindow) as chunkList, node, score
              UNWIND chunkList as chunkRows
            WITH collect(chunkRows.text) as textList, node, score
            RETURN apoc.text.join(textList, " \\n ") as text, score
            ORDER BY score DESC
            """
            
            results = self.kg.query(window_query, params={
                'character': character,
                'queryVector': query_embedding,
                'limit': limit
            })
            
            return [result['text'] for result in results]
            
        except Exception as e:
            print(f"Error finding character context with window: {e}")
            return []

    def find_character_context_with_relationships(self, character: str, user_input: str, limit: int = 3) -> List[str]:
        """Find character context including relationship information (L5 approach) using Cohere"""
        try:
            # Get Cohere embedding for user input
            query_embedding = self.get_cohere_embedding(user_input)
            if not query_embedding:
                return []
            
            # Enhanced retrieval with relationship context
            relationship_query = f"""
            MATCH (chunk:Chunk)-[:MENTIONED_IN]->(char:Character {{name: $character}})
            WITH chunk, $queryVector AS queryVector
            CALL db.index.vector.queryNodes('{self.VECTOR_INDEX_NAME}', $limit, queryVector) 
            YIELD node, score
            WHERE node = chunk
            WITH node, score
            OPTIONAL MATCH (node)-[:PART_OF]->(book:Book)
            OPTIONAL MATCH (node)-[:MENTIONED_IN]->(char:Character)
            WITH node, score, book, collect(char.name) as mentionedChars
            WITH node, score, 
                 "Book: " + book.title + " | Characters: " + apoc.text.join(mentionedChars, ", ") as contextInfo
            RETURN contextInfo + "\\n\\n" + node.text as text, score
            ORDER BY score DESC
            """
            
            results = self.kg.query(relationship_query, params={
                'character': character,
                'queryVector': query_embedding,
                'limit': limit
            })
            
            return [result['text'] for result in results]
            
        except Exception as e:
            print(f"Error finding character context with relationships: {e}")
            return []

    def get_character_style(self, character: str) -> Dict[str, Any]:
        """Get character style from knowledge graph"""
        try:
            query = """
            MATCH (char:Character {name: $character})
            RETURN char.personality as personality,
                   char.speechPattern as speechPattern,
                   char.keyPhrases as keyPhrases,
                   char.dialogueStyle as dialogueStyle,
                   char.emotionalRange as emotionalRange
            """
            
            result = self.kg.query(query, params={'character': character})
            if result:
                return result[0]
            return {}
        except Exception as e:
            print(f"Error getting character style: {e}")
            return {}

    def generate_character_response(self, character: str, user_input: str, context: List[str]) -> str:
        """Generate character response using Cohere with character-specific style"""
        # Get character style from KG
        character_style = self.get_character_style(character)
        
        # Build context string
        context_text = "\n\n".join(context) if context else "No specific context available."
        
        # Create character-specific prompt
        system_prompt = f"""
You are {character} from the book.

Character Profile (from book analysis):
- Personality: {character_style.get('personality', 'mysterious')}
- Speech Pattern: {character_style.get('speechPattern', 'formal')}
- Key Phrases: {', '.join(character_style.get('keyPhrases', []))}
- Dialogue Style: {character_style.get('dialogueStyle', 'conversational')}
- Emotional Range: {character_style.get('emotionalRange', 'varied')}

Context from the book:
{context_text}

Guidelines:
- Stay completely in character as {character}
- Use their specific speech patterns and personality from the book
- Reference events and relationships from the book when relevant
- Keep responses natural and conversational
- Don't break character or mention you're an AI
- If you don't know something specific, respond as {character} would
"""

        try:
            response = self.cohere_client.chat(
                model="command-a-03-2025",
                message=user_input,
                preamble=system_prompt,
                temperature=0.7,
                max_tokens=300
            )
            return response.text.strip()
        except Exception as e:
            print(f"Error generating response: {e}")
            return f"I'm sorry, I can't respond right now. (Error: {e})"

    def setup_langchain_retrieval_chains(self):
        """Setup LangChain retrieval chains using L4/L5 approaches with Cohere"""
        print("🔗 Setting up LangChain chains with Cohere...")
        
        # Create a custom Cohere embedding class for LangChain
        class CohereEmbeddings:
            def __init__(self, cohere_client):
                self.cohere_client = cohere_client
            
            def embed_documents(self, texts):
                try:
                    response = self.cohere_client.embed(
                        texts=texts,
                        model="embed-english-v3.0",
                        input_type="search_document"
                    )
                    return response.embeddings
                except Exception as e:
                    print(f"Error embedding documents: {e}")
                    return []
            
            def embed_query(self, text):
                try:
                    response = self.cohere_client.embed(
                        texts=[text],
                        model="embed-english-v3.0",
                        input_type="search_query"
                    )
                    return response.embeddings[0]
                except Exception as e:
                    print(f"Error embedding query: {e}")
                    return []
        
        # Create Cohere embeddings instance
        cohere_embeddings = CohereEmbeddings(self.cohere_client)
        
        # Basic vector store (L4 approach)
        basic_vector_store = Neo4jVector.from_existing_graph(
            embedding=cohere_embeddings,
            url=self.NEO4J_URI,
            username=self.NEO4J_USERNAME,
            password=self.NEO4J_PASSWORD,
            index_name=self.VECTOR_INDEX_NAME,
            node_label=self.VECTOR_NODE_LABEL,
            text_node_properties=[self.VECTOR_SOURCE_PROPERTY],
            embedding_node_property=self.VECTOR_EMBEDDING_PROPERTY,
        )
        
        # Windowed retrieval query (L5 approach)
        windowed_retrieval_query = """
        MATCH window = (:Chunk)-[:NEXT*0..1]->(node)-[:NEXT*0..1]->(:Chunk)
        WITH node, score, window as longestWindow 
          ORDER BY length(window) DESC LIMIT 1
        WITH nodes(longestWindow) as chunkList, node, score
          UNWIND chunkList as chunkRows
        WITH collect(chunkRows.text) as textList, node, score
        RETURN apoc.text.join(textList, " \\n ") as text,
            score,
            node {.source, .bookTitle, .charactersMentioned} AS metadata
        """
        
        windowed_vector_store = Neo4jVector.from_existing_index(
            embedding=cohere_embeddings,
            url=self.NEO4J_URI,
            username=self.NEO4J_USERNAME,
            password=self.NEO4J_PASSWORD,
            database=self.NEO4J_DATABASE,
            index_name=self.VECTOR_INDEX_NAME,
            text_node_property=self.VECTOR_SOURCE_PROPERTY,
            retrieval_query=windowed_retrieval_query,
        )
        
        # Enhanced retrieval with character context (L5 approach)
        character_retrieval_query = """
        MATCH (node)-[:MENTIONED_IN]->(char:Character)
        WITH node, score, collect(char.name) as mentionedChars
        MATCH window = (:Chunk)-[:NEXT*0..1]->(node)-[:NEXT*0..1]->(:Chunk)
        WITH node, score, mentionedChars, window as longestWindow 
          ORDER BY length(window) DESC LIMIT 1
        WITH nodes(longestWindow) as chunkList, node, score, mentionedChars
          UNWIND chunkList as chunkRows
        WITH collect(chunkRows.text) as textList, node, score, mentionedChars
        RETURN apoc.text.join(textList, " \\n ") as text,
            score,
            node {.source, .bookTitle, .charactersMentioned} AS metadata,
            "Characters in context: " + apoc.text.join(mentionedChars, ", ") as characterContext
        """
        
        character_vector_store = Neo4jVector.from_existing_index(
            embedding=cohere_embeddings,
            url=self.NEO4J_URI,
            username=self.NEO4J_USERNAME,
            password=self.NEO4J_PASSWORD,
            database=self.NEO4J_DATABASE,
            index_name=self.VECTOR_INDEX_NAME,
            text_node_property=self.VECTOR_SOURCE_PROPERTY,
            retrieval_query=character_retrieval_query,
        )
        
        # Create retrievers
        basic_retriever = basic_vector_store.as_retriever()
        windowed_retriever = windowed_vector_store.as_retriever()
        character_retriever = character_vector_store.as_retriever()
        
        # Create QA chains
        basic_chain = RetrievalQAWithSourcesChain.from_chain_type(
            ChatOpenAI(temperature=0), 
            chain_type="stuff", 
            retriever=basic_retriever
        )
        
        windowed_chain = RetrievalQAWithSourcesChain.from_chain_type(
            ChatOpenAI(temperature=0), 
            chain_type="stuff", 
            retriever=windowed_retriever
        )
        
        character_chain = RetrievalQAWithSourcesChain.from_chain_type(
            ChatOpenAI(temperature=0), 
            chain_type="stuff", 
            retriever=character_retriever
        )
        
        return basic_chain, windowed_chain, character_chain

    def chat_with_character(self, character: str, user_input: str, use_advanced_retrieval: bool = True) -> str:
        """Main function to chat with any character using L4/L5 approaches"""
        print(f"\n📚 Chatting with {character}...")
        
        if use_advanced_retrieval:
            # Try windowed retrieval first (L5 approach)
            context = self.find_character_context_with_window(character, user_input)
            if not context:
                # Fallback to relationship-enhanced retrieval
                context = self.find_character_context_with_relationships(character, user_input)
        else:
            # Basic vector search (L4 approach)
            context = self.find_character_context(character, user_input)
        
        # Generate response
        response = self.generate_character_response(character, user_input, context)
        
        return response

    def chat_with_character_using_langchain(self, character: str, user_input: str) -> str:
        """Chat using LangChain chains (L4/L5 integration)"""
        print(f"\n🔗 Chatting with {character} using LangChain...")
        
        # Setup chains
        basic_chain, windowed_chain, character_chain = self.setup_langchain_retrieval_chains()
        
        if not all([basic_chain, windowed_chain, character_chain]):
            return "LangChain chains not available. Please check embeddings setup."
        
        # Try character-specific chain first
        try:
            # Add character context to the question
            enhanced_question = f"Answer as {character}: {user_input}"
            response = character_chain({"question": enhanced_question}, return_only_outputs=True)
            return response.get('answer', 'No response generated')
        except Exception as e:
            print(f"Character chain failed: {e}")
            
            # Fallback to windowed chain
            try:
                response = windowed_chain({"question": user_input}, return_only_outputs=True)
                return response.get('answer', 'No response generated')
            except Exception as e2:
                print(f"Windowed chain failed: {e2}")
                
                # Final fallback to basic chain
                try:
                    response = basic_chain({"question": user_input}, return_only_outputs=True)
                    return response.get('answer', 'No response generated')
                except Exception as e3:
                    print(f"Basic chain failed: {e3}")
                    return "All retrieval methods failed."

    def setup_book_kg(self, pdf_path: str, book_title: str, book_author: str = "Unknown"):
        """Complete setup of book knowledge graph"""
        print(f"📖 Setting up Knowledge Graph for: {book_title}")
        
        # Extract text from PDF
        print("📄 Extracting text from PDF...")
        text = self.extract_text_from_pdf(pdf_path)
        if not text:
            print("❌ Failed to extract text from PDF")
            return False
            
        # Split into chunks
        print("✂️ Splitting text into chunks...")
        chunks = self.split_book_text(text, book_title, book_author)
        
        # Create nodes and relationships
        print("🏗️ Creating knowledge graph with LLM analysis...")
        self.create_chunk_nodes(chunks)
        self.create_character_nodes(chunks)
        self.create_relationships(chunks)
        
        # Create vector index
        if self.embeddings:
            print("🧠 Creating vector index...")
            self.create_vector_index()
        
        print("✅ Book Knowledge Graph setup complete!")
        return True

    def list_available_characters(self) -> List[str]:
        """List available characters for chatting"""
        try:
            query = """
            MATCH (char:Character)
            RETURN char.name as name
            ORDER BY char.name
            """
            results = self.kg.query(query)
            return [result['name'] for result in results]
        except Exception as e:
            print(f"Error listing characters: {e}")
            return []

    def get_character_info(self, character: str) -> Dict:
        """Get detailed information about a character"""
        try:
            query = """
            MATCH (char:Character {name: $character})
            RETURN char
            """
            result = self.kg.query(query, params={'character': character})
            if result:
                return dict(result[0]['char'])
            return {}
        except Exception as e:
            print(f"Error getting character info: {e}")
            return {}

    def get_character_merge_statistics(self) -> Dict:
        """Get statistics about character merging and deduplication"""
        try:
            # Get total character count
            total_chars_query = """
            MATCH (char:Character)
            RETURN count(char) as total_characters
            """
            total_result = self.kg.query(total_chars_query)
            total_characters = total_result[0]['total_characters'] if total_result else 0
            
            # Get characters with mentions
            mentioned_chars_query = """
            MATCH (char:Character)-[:MENTIONED_IN]->(chunk:Chunk)
            RETURN count(DISTINCT char) as mentioned_characters
            """
            mentioned_result = self.kg.query(mentioned_chars_query)
            mentioned_characters = mentioned_result[0]['mentioned_characters'] if mentioned_result else 0
            
            # Get characters with detailed analysis
            analyzed_chars_query = """
            MATCH (char:Character)
            WHERE char.personality IS NOT NULL AND char.personality <> ''
            RETURN count(char) as analyzed_characters
            """
            analyzed_result = self.kg.query(analyzed_chars_query)
            analyzed_characters = analyzed_result[0]['analyzed_characters'] if analyzed_result else 0
            
            return {
                'total_characters': total_characters,
                'mentioned_characters': mentioned_characters,
                'analyzed_characters': analyzed_characters,
                'deduplication_applied': True
            }
        except Exception as e:
            print(f"Error getting character statistics: {e}")
            return {}

    def get_book_info(self) -> Dict:
        """Get information about the book"""
        try:
            query = """
            MATCH (chunk:Chunk)
            RETURN DISTINCT chunk.bookTitle as title, chunk.bookAuthor as author
            LIMIT 1
            """
            result = self.kg.query(query)
            if result:
                return result[0]
            return {}
        except Exception as e:
            print(f"Error getting book info: {e}")
            return {}

# Example usage
def main():
    """Example usage of the Generic Book KG system"""
    system = GenericBookKGSystem()
    
    # Example: Setup Harry Potter
    # system.setup_book_kg("harry_potter.pdf", "Harry Potter and the Philosopher's Stone", "J.K. Rowling")
    
    # List available characters
    print("Available characters:")
    for char in system.list_available_characters():
        print(f"- {char}")

if __name__ == "__main__":
    main()

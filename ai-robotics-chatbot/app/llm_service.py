"""LLM and embedding utilities with multi-provider support (OpenAI + Google Gemini + Anthropic Claude)."""

from openai import AsyncOpenAI
from typing import List
import asyncio
import importlib

from config import settings


# Try to import Google generative AI SDK if available
try:
    import google.generativeai as genai
    GENAI_AVAILABLE = True
except Exception:
    genai = None
    GENAI_AVAILABLE = False


# Try to import Anthropic Claude SDK if available
try:
    import anthropic
    CLAUDE_AVAILABLE = True
except Exception:
    anthropic = None
    CLAUDE_AVAILABLE = False


class EmbeddingService:
    """Service for generating embeddings (OpenAI embeddings used by default)."""
    
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)
        self.model = settings.embedding_model
    
    async def embed_text(self, text: str) -> List[float]:
        try:
            response = await self.client.embeddings.create(
                input=text,
                model=self.model
            )
            return response.data[0].embedding
        except Exception as e:
            print(f"Warning: Embedding service failed: {e}")
            # Deterministic fallback embedding
            import hashlib, random
            hash_val = hashlib.md5(text.encode()).hexdigest()
            seed = int(hash_val, 16) % (2**32)
            random.seed(seed)
            return [random.random() for _ in range(1536)]


class RAGChatService:
    """RAG chat service with support for multiple LLM providers (OpenAI, Google Gemini, Anthropic Claude).

    Implementation attempts to use the configured provider (Gemini or Claude) when enabled.
    If the primary provider fails or SDK is not available, it falls back to OpenAI or to the local fallback.
    
    Supported providers:
    - 'openai': OpenAI GPT models (default fallback)
    - 'google': Google Gemini (generative AI)
    - 'claude': Anthropic Claude
    """

    def __init__(self):
        # Initialize OpenAI client (used for embeddings/fallback)
        self.openai_client = AsyncOpenAI(api_key=settings.openai_api_key)
        self.openai_model = settings.chat_model
        self.provider = settings.llm_provider.lower() if settings.llm_provider else "openai"
        self.last_model_used = None  # Track which model was actually used

        # Configure Gemini if requested and SDK present
        self.gemini_enabled = False
        if self.provider == "google" and GENAI_AVAILABLE and settings.gemini_api_key:
            try:
                genai.configure(api_key=settings.gemini_api_key)
                self.gemini_enabled = True
                print("Gemini SDK configured")
            except Exception as e:
                print(f"Failed to configure Gemini SDK: {e}")

        # Configure Claude if requested and SDK present
        self.claude_enabled = False
        self.claude_client = None
        if self.provider == "claude" and CLAUDE_AVAILABLE and settings.claude_api_key:
            try:
                self.claude_client = anthropic.Anthropic(api_key=settings.claude_api_key)
                self.claude_enabled = True
                print("Claude SDK configured")
            except Exception as e:
                print(f"Failed to configure Claude SDK: {e}")

    async def generate_response(
        self,
        query: str,
        context_documents: List[dict],
        conversation_history: List[dict] = None
    ) -> str:
        # Build context
        context = "\n\n".join([
            f"Source: {doc.get('source', 'Unknown')}\n{doc.get('text', '')}"
            for doc in context_documents
        ]) if context_documents else "No context from textbook available."

        system_prompt = f"""You are an AI assistant specialized in physical AI and humanoid robotics.
You have access to the AI Robotics Textbook content.

When answering questions:
1. Use the provided context from the textbook
2. Be accurate and cite specific sections when relevant
3. Explain concepts clearly for both beginners and advanced readers
4. If the information is not in the context, indicate that it's beyond the textbook scope
5. Provide code examples when relevant
6. Be concise but thorough

Context from the textbook:
{context}"""

        # Choose provider
        if self.provider == "google" and self.gemini_enabled:
            try:
                # Use Gemini's generate_content API (correct API)
                try:
                    model = genai.GenerativeModel('gemini-pro')
                    prompt_text = f"{system_prompt}\n\nUser: {query}"
                    response = model.generate_content(prompt_text)
                    if response.text:
                        print(f"[GEMINI SUCCESS] Got response from Gemini API")
                        self.last_model_used = "gemini-pro"
                        return response.text
                except Exception as e1:
                    print(f"[GEMINI ERROR 1] First attempt failed: {e1}")
                    # Try alternative approach with just the query
                    try:
                        model = genai.GenerativeModel('gemini-pro')
                        response = model.generate_content(query)
                        if response.text:
                            print(f"[GEMINI SUCCESS] Got response from Gemini API (alt)")
                            self.last_model_used = "gemini-pro"
                            return response.text
                    except Exception as e2:
                        print(f"[GEMINI ERROR 2] Alternative attempt failed: {e2}")
            except Exception as e:
                print(f"[GEMINI CRITICAL ERROR] {e}")
                # Fall through to Claude/OpenAI/fallback

        # Try Claude if enabled
        if self.provider == "claude" and self.claude_enabled and self.claude_client:
            try:
                response = self.claude_client.messages.create(
                    model="claude-3-sonnet-20240229",
                    max_tokens=2048,
                    system=system_prompt,
                    messages=[{"role": "user", "content": query}]
                )
                if response.content and len(response.content) > 0:
                    self.last_model_used = "claude-3-sonnet-20240229"
                    return response.content[0].text
            except Exception as e:
                print(f"Claude API error: {e}")
                # Fall through to OpenAI/fallback

        # Default: use OpenAI via AsyncOpenAI (best-effort)
        try:
            messages = [{"role": "system", "content": system_prompt}]
            if conversation_history:
                messages.extend(conversation_history)
            messages.append({"role": "user", "content": query})

            response = await self.openai_client.messages.create(
                model=self.openai_model,
                max_tokens=settings.max_tokens,
                temperature=settings.temperature,
                messages=messages
            )
            self.last_model_used = self.openai_model
            return response.content[0].text
        except Exception as e:
            print(f"OpenAI API error or fallback needed: {e}")
            # Use the built-in fallback knowledge base
            self.last_model_used = "(Fallback)"
            return self._generate_fallback_response(query, context)

    def _generate_fallback_response(self, query: str, context: str) -> str:
        query_lower = query.lower()
        responses = {
            "robot": "A robot is an autonomous or semi-autonomous machine designed to perform tasks. Robots can vary from industrial manufacturing systems to humanoid robots that mimic human movement and interaction.",
            "humanoid": "Humanoid robots are robots designed to resemble and function like humans. They typically have two arms, two legs, a torso, and a head, enabling them to navigate human environments and interact naturally with people.",
            "degree": "Degrees of freedom (DOF) refer to the number of independent movements a robot can make. For example, a robot arm with 6 DOF can move in 3D space and rotate around 3 axes.",
            "perception": "Robot perception involves using sensors (cameras, LIDAR, tactile sensors) to understand the environment. This enables robots to locate objects, detect obstacles, and interact safely with their surroundings.",
            "motion": "Motion planning is the process of computing a path for a robot to move from one position to another while avoiding obstacles. Common algorithms include RRT (Rapidly-exploring Random Tree) and A*.",
            "learning": "Deep learning enables robots to process visual and sensor data to recognize patterns, objects, and behaviors. Convolutional Neural Networks (CNNs) are commonly used for vision tasks.",
            "application": "Robotics applications range from manufacturing, healthcare, agriculture, exploration, entertainment, and service industries. Robots increase efficiency, safety, and enable tasks in hazardous environments.",
        }
        for key, response_text in responses.items():
            if key in query_lower:
                return response_text
        return f"I'm an AI assistant for the AI Robotics Textbook. (Fallback) Your question: '{query}'"

    async def generate_response_with_selection(self, query: str, selected_text: str) -> str:
        system_prompt = f"""You are an AI assistant specialized in physical AI and humanoid robotics.
A user has selected the following text from the AI Robotics Textbook and asked a question about it:

SELECTED TEXT:
{selected_text}

Answer the user's question based on this selected text and your knowledge of robotics.
Be specific and reference the selected text in your answer."""
        # Try Gemini if enabled
        if self.provider == "google" and self.gemini_enabled:
            try:
                model = genai.GenerativeModel('gemini-pro')
                prompt_text = f"{system_prompt}\n\nUser: {query}"
                response = model.generate_content(prompt_text)
                if response.text:
                    self.last_model_used = "gemini-pro"
                    return response.text
            except Exception as e:
                print(f"Gemini selection call failed: {e}")

        # Try Claude if enabled
        if self.provider == "claude" and self.claude_enabled and self.claude_client:
            try:
                response = self.claude_client.messages.create(
                    model="claude-3-sonnet-20240229",
                    max_tokens=2048,
                    system=system_prompt,
                    messages=[{"role": "user", "content": query}]
                )
                if response.content and len(response.content) > 0:
                    self.last_model_used = "claude-3-sonnet-20240229"
                    return response.content[0].text
            except Exception as e:
                print(f"Claude selection call failed: {e}")

        # Fall back to OpenAI style invocation
        try:
            messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": query}]
            response = await self.openai_client.messages.create(
                model=self.openai_model,
                max_tokens=settings.max_tokens,
                temperature=settings.temperature,
                messages=messages
            )
            self.last_model_used = self.openai_model
            return response.content[0].text
        except Exception as e:
            print(f"Fallback selection generation failed: {e}")
            self.last_model_used = "(Fallback)"
            return f"Based on the selected text:\n{selected_text}\n\nYour question: {query}\n\n(Fallback response)"


# Global instances
embedding_service = EmbeddingService()
rag_chat_service = RAGChatService()

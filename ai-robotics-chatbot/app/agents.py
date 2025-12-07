"""Subagent framework for composable AI capabilities."""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict


@dataclass
class AgentResponse:
    """Standard response format for all subagents."""
    status: str  # "success" or "error"
    result: Any
    metadata: Dict[str, Any]
    error: Optional[str] = None


class SubagentBase(ABC):
    """Abstract base class for all subagents."""

    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description

    @abstractmethod
    async def invoke(self, query: str, context: Optional[Dict[str, Any]] = None) -> AgentResponse:
        """Invoke the subagent with a query and optional context."""
        pass

    @abstractmethod
    def metadata(self) -> Dict[str, Any]:
        """Return metadata about this subagent."""
        pass


class DocumentSearchAgent(SubagentBase):
    """Search and retrieve relevant documents from the textbook."""

    def __init__(self, vector_db=None):
        super().__init__(
            name="document_search",
            description="Searches the AI Robotics Textbook for relevant documents and context"
        )
        self.vector_db = vector_db

    async def invoke(self, query: str, context: Optional[Dict[str, Any]] = None) -> AgentResponse:
        """Search for documents related to the query."""
        try:
            if not self.vector_db:
                return AgentResponse(
                    status="error",
                    result=[],
                    metadata={"agent": self.name, "search_query": query},
                    error="Vector DB not initialized"
                )

            # Simulate document search (in production, would call actual vector DB)
            documents = [
                {
                    "id": "doc_001",
                    "title": "Introduction to Robotics",
                    "text": "Robotics is the field of engineering and computer science focused on designing, building, and operating robots.",
                    "score": 0.95,
                    "source": "Chapter 1: Fundamentals"
                },
                {
                    "id": "doc_002",
                    "title": "Humanoid Robots",
                    "text": "Humanoid robots are designed to resemble human form and behavior, with two arms, two legs, and a torso.",
                    "score": 0.87,
                    "source": "Chapter 5: Humanoid Robotics"
                }
            ]

            return AgentResponse(
                status="success",
                result=documents,
                metadata={
                    "agent": self.name,
                    "search_query": query,
                    "documents_retrieved": len(documents),
                    "top_scores": [d["score"] for d in documents[:3]]
                }
            )
        except Exception as e:
            return AgentResponse(
                status="error",
                result=[],
                metadata={"agent": self.name},
                error=str(e)
            )

    def metadata(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "capabilities": ["document_search", "context_retrieval", "semantic_ranking"]
        }


class CodeAgent(SubagentBase):
    """Generate code snippets for robotics problems."""

    def __init__(self):
        super().__init__(
            name="code_agent",
            description="Generates Python code snippets for robotics applications"
        )

    async def invoke(self, query: str, context: Optional[Dict[str, Any]] = None) -> AgentResponse:
        """Generate code for the given robotics problem."""
        try:
            # Generate template-based code
            code_snippets = {
                "robot": """
# Basic Robot Class
class Robot:
    def __init__(self, name: str, dof: int):
        self.name = name
        self.degrees_of_freedom = dof
        self.position = [0, 0, 0]
    
    def move(self, x: float, y: float, z: float):
        self.position = [x, y, z]
        print(f"{self.name} moved to {self.position}")
                """,
                "humanoid": """
# Humanoid Robot Class
class HumanoidRobot:
    def __init__(self, name: str):
        self.name = name
        self.arms = {"left": [], "right": []}
        self.legs = {"left": [], "right": []}
    
    def walk(self, steps: int):
        print(f"{self.name} walking {steps} steps")
    
    def pick_up(self, object_name: str):
        print(f"{self.name} picking up {object_name}")
                """,
                "motion": """
# Motion Planning Example
import numpy as np

def plan_path(start, goal, obstacles):
    '''Simple RRT-based path planning'''
    path = [start]
    current = start
    while np.linalg.norm(np.array(current) - np.array(goal)) > 0.1:
        random_point = np.random.rand(3)
        current = move_towards(current, random_point, 0.1)
        path.append(current)
    path.append(goal)
    return path
                """
            }

            # Find relevant code snippet
            matched_code = code_snippets.get(query.lower().split()[0] if query else "", "# No code available")

            return AgentResponse(
                status="success",
                result={"code": matched_code},
                metadata={
                    "agent": self.name,
                    "query": query,
                    "language": "python",
                    "type": "template"
                }
            )
        except Exception as e:
            return AgentResponse(
                status="error",
                result={},
                metadata={"agent": self.name},
                error=str(e)
            )

    def metadata(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "capabilities": ["code_generation", "template_synthesis", "python_support"]
        }


class CitationAgent(SubagentBase):
    """Format and manage citations and references."""

    def __init__(self):
        super().__init__(
            name="citation_agent",
            description="Formats citations and manages references from the textbook"
        )

    async def invoke(self, query: str, context: Optional[Dict[str, Any]] = None) -> AgentResponse:
        """Format citations for the given sources."""
        try:
            citations = []
            if context and "documents" in context:
                for doc in context["documents"]:
                    citation = {
                        "id": doc.get("id", "unknown"),
                        "title": doc.get("title", "Untitled"),
                        "source": doc.get("source", "Unknown"),
                        "format": {
                            "footnote": f"[{doc.get('source', 'Src')}]",
                            "inline": f"{doc.get('source', 'Source')} (pg. 1-50)",
                            "full": f"{doc.get('title', 'Doc')}. From {doc.get('source', 'AI Robotics Textbook')}"
                        }
                    }
                    citations.append(citation)

            return AgentResponse(
                status="success",
                result={"citations": citations},
                metadata={
                    "agent": self.name,
                    "total_citations": len(citations),
                    "formats": ["footnote", "inline", "full"]
                }
            )
        except Exception as e:
            return AgentResponse(
                status="error",
                result={},
                metadata={"agent": self.name},
                error=str(e)
            )

    def metadata(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "capabilities": ["citation_formatting", "reference_management", "footnotes"]
        }


class SubagentRegistry:
    """Registry for discovering and dispatching subagents."""

    def __init__(self):
        self.agents: Dict[str, SubagentBase] = {}

    def register(self, agent: SubagentBase) -> None:
        """Register a subagent."""
        self.agents[agent.name] = agent

    def get(self, name: str) -> Optional[SubagentBase]:
        """Get a subagent by name."""
        return self.agents.get(name)

    def list_all(self) -> List[Dict[str, Any]]:
        """List all registered subagents with metadata."""
        return [agent.metadata() for agent in self.agents.values()]

    async def invoke(self, agent_name: str, query: str, context: Optional[Dict[str, Any]] = None) -> AgentResponse:
        """Invoke a subagent by name."""
        agent = self.get(agent_name)
        if not agent:
            return AgentResponse(
                status="error",
                result={},
                metadata={"requested_agent": agent_name},
                error=f"Agent '{agent_name}' not found"
            )
        return await agent.invoke(query, context)


# Global registry
_subagent_registry: Optional[SubagentRegistry] = None


def initialize_subagents(vector_db=None) -> SubagentRegistry:
    """Initialize all subagents and return the registry."""
    global _subagent_registry
    
    registry = SubagentRegistry()
    
    # Register subagents
    registry.register(DocumentSearchAgent(vector_db=vector_db))
    registry.register(CodeAgent())
    registry.register(CitationAgent())
    
    _subagent_registry = registry
    return registry


def get_subagent_registry() -> SubagentRegistry:
    """Get the global subagent registry."""
    global _subagent_registry
    if _subagent_registry is None:
        _subagent_registry = initialize_subagents()
    return _subagent_registry

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class AgentMessage(BaseModel):
    role: str
    content: str


class ToolResult(BaseModel):
    tool_name: str
    success: bool
    summary: str
    data: Dict[str, Any] = Field(default_factory=dict)


class AgentState(BaseModel):
    # Conversation
    messages: List[AgentMessage] = Field(default_factory=list)

    # Understanding
    
    session_id: Optional[str] = None
    previous_state: Dict[str, Any] = Field(default_factory=dict)  

    language: str = "English"
    script: str = "Latin"
    input_type: str = "text"
    input_file_path: Optional[str] = None
    intent: Optional[str] = None
    user_goal: Optional[str] = None
    context: Dict[str, Any] = Field(default_factory=dict)

    # Investigation
    selected_tools: List[str] = Field(default_factory=list)
    tool_results: List[ToolResult] = Field(default_factory=list)

    # Intelligence
    situation: Optional[str] = None
    risk_score: int = 0
    risk_level: str = "Unknown"
    risk_factors: List[str] = Field(default_factory=list)
    consequences: List[str] = Field(default_factory=list)

    # Resolution
    action_plan: List[str] = Field(default_factory=list)
    things_to_avoid: List[str] = Field(default_factory=list)
    what_to_do: List[str] = Field(default_factory=list)
    what_not_to_do: List[str] = Field(default_factory=list)

    # Agent execution
    current_step: Optional[str] = None
    agent_activity: List[str] = Field(default_factory=list)
    needs_follow_up: bool = False
    follow_up_questions: List[str] = Field(default_factory=list)

    # Evaluation
    evaluation_status: str = "pending"
    adaptation_required: bool = False
    confidence: float = 0.0
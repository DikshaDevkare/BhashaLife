import shutil
import uuid
from pathlib import Path
from typing import Dict, Optional

from fastapi import FastAPI, File, Form, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from app.agents.orchestrator import AgentOrchestrator
from app.models.schemas import AgentMessage, AgentState


# ==============================================================
# APP
# ==============================================================

app = FastAPI(
    title="BhashaLife AI",
    description="Your Multilingual Life & Digital Safety Agent",
    version="1.0.0",
)


# ==============================================================
# CORS
# ==============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==============================================================
# UPLOADS
# ==============================================================

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


# ==============================================================
# SESSION STORE
# ==============================================================

# Lightweight in-memory session storage for the hackathon demo.
#
# Important behavior:
#
# 1. New file/screenshot = NEW investigation/session.
# 2. Text message with existing session = FOLLOW-UP.
#
# This allows us to preserve adaptive conversations while
# preventing one uploaded document from contaminating another.

SESSIONS: Dict[str, AgentState] = {}


# ==============================================================
# ROOT
# ==============================================================

@app.get("/")
def root():
    return {
        "name": "BhashaLife AI",
        "status": "online",
        "message": (
            "Understand what matters. "
            "Know what to do next."
        ),
    }


# ==============================================================
# HEALTH
# ==============================================================

@app.get("/health")
def health():
    return {
        "status": "healthy",
        "service": "bhashalife-backend",
        "active_sessions": len(SESSIONS),
    }


# ==============================================================
# HELPER — CREATE SESSION
# ==============================================================

def create_session() -> str:
    """
    Create a unique conversation session.
    """
    return str(uuid.uuid4())


# ==============================================================
# HELPER — SAVE UPLOAD
# ==============================================================

def save_upload(
    file: UploadFile,
) -> str:
    """
    Save an uploaded file and return its path.
    """

    safe_name = Path(
        file.filename or "uploaded_file"
    ).name

    # Unique prefix prevents files with the same name
    # from overwriting each other.
    unique_name = (
        f"{uuid.uuid4().hex[:8]}_{safe_name}"
    )

    file_path = UPLOAD_DIR / unique_name

    with file_path.open("wb") as buffer:
        shutil.copyfileobj(
            file.file,
            buffer,
        )

    return str(file_path)


# ==============================================================
# HELPER — DETECT INPUT TYPE
# ==============================================================

def detect_input_type(
    file: Optional[UploadFile],
) -> str:
    """
    Determine whether the uploaded input is an image
    or a document.
    """

    if not file:
        return "text"

    filename = (
        file.filename or ""
    ).lower()

    if filename.endswith(
        (
            ".png",
            ".jpg",
            ".jpeg",
            ".webp",
            ".bmp",
        )
    ):
        return "image"

    if filename.endswith(
        (
            ".pdf",
            ".txt",
            ".doc",
            ".docx",
        )
    ):
        return "document"

    # Unknown uploaded formats are treated as documents
    # so the agent can handle them gracefully.
    return "document"


# ==============================================================
# ANALYZE
# ==============================================================

@app.post("/api/analyze")
async def analyze(
    text: str = Form(""),
    context: str = Form(""),
    language: str = Form("English"),
    session_id: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
):
    """
    Main BhashaLife AI endpoint.

    --------------------------------------------------------------
    NEW INVESTIGATION
    --------------------------------------------------------------

    Uploading a new file always starts a fresh investigation.

        PDF A
          ↓
        Session A

        PDF B
          ↓
        Session B

    This prevents PDF A's deadline/action/requirements from
    appearing in PDF B's report.

    --------------------------------------------------------------
    ADAPTIVE FOLLOW-UP
    --------------------------------------------------------------

    A text-only message with an existing session continues
    that conversation.

        PDF A
          ↓
        Session A
          ↓
        "I don't have my Bonafide Certificate."
          ↓
        Previous state loaded
          ↓
        Agent adapts/replans

    --------------------------------------------------------------
    """

    # ==========================================================
    # CLEAN INPUT
    # ==========================================================

    user_text = text.strip()

    # ==========================================================
    # DETECT INPUT TYPE
    # ==========================================================

    input_type = detect_input_type(file)

    input_file_path: Optional[str] = None

    # ==========================================================
    # SAVE FILE
    # ==========================================================

    if file:
        input_file_path = save_upload(file)

    # ==========================================================
    # DETERMINE WHETHER THIS IS A FOLLOW-UP
    # ==========================================================

    is_follow_up = (
        file is None
        and session_id is not None
        and session_id in SESSIONS
        and bool(user_text)
    )

    # ==========================================================
    # FOLLOW-UP REQUEST
    # ==========================================================

    if is_follow_up:

        previous_state = SESSIONS[session_id]

        # Deep copy previous state using Pydantic.
        state = AgentState.model_validate(
            previous_state.model_dump()
        )

        state.session_id = session_id

        # Keep a snapshot of the previous state so the
        # evaluator/adaptation logic can compare context.
        state.previous_state = (
            previous_state.model_dump()
        )

        # ------------------------------------------------------
        # Add new user message
        # ------------------------------------------------------

        state.messages.append(
            AgentMessage(
                role="user",
                content=user_text,
            )
        )

        # ------------------------------------------------------
        # Mark this as new information
        # ------------------------------------------------------

        state.agent_activity.append(
            "New information received"
        )

        state.agent_activity.append(
            "Previous agent state retrieved"
        )

        # ------------------------------------------------------
        # Mark adaptive follow-up
        # ------------------------------------------------------

        state.context["is_follow_up"] = True

        state.adaptation_required = True

        # ------------------------------------------------------
        # Update user context if supplied
        # ------------------------------------------------------

        if context.strip():
            state.context["user_context"] = (
                context.strip()
            )

    # ==========================================================
    # NEW INVESTIGATION
    # ==========================================================

    else:

        # A new investigation always receives a new session ID.
        session_id = create_session()

        # ------------------------------------------------------
        # Create initial user message
        # ------------------------------------------------------

        if user_text:

            user_message = user_text

        elif file:

            input_label = (
                "screenshot"
                if input_type == "image"
                else "document"
            )

            user_message = (
                f"Analyze the uploaded "
                f"{input_label}: "
                f"{file.filename}"
            )

        else:

            user_message = ""

        # ------------------------------------------------------
        # Create completely fresh agent state
        # ------------------------------------------------------

        state = AgentState(
            session_id=session_id,
            language=language,
            input_type=input_type,
            input_file_path=input_file_path,
            messages=[
                AgentMessage(
                    role="user",
                    content=user_message,
                )
            ]
            if user_message
            else [],
        )

        # ------------------------------------------------------
        # Store user context
        # ------------------------------------------------------

        if context.strip():
            state.context["user_context"] = (
                context.strip()
            )

        # ------------------------------------------------------
        # Explicit document intent
        # ------------------------------------------------------

        if input_type == "document":

            state.intent = (
                "document_guidance"
            )

            state.user_goal = (
                "Understand the document "
                "and determine the required "
                "next steps"
            )

        # ------------------------------------------------------
        # Explicit image intent
        # ------------------------------------------------------

        elif input_type == "image":

            state.intent = (
                "digital_safety"
            )

            state.user_goal = (
                "Understand the uploaded "
                "image and determine "
                "whether action is required"
            )

        # ------------------------------------------------------
        # This is NOT a follow-up
        # ------------------------------------------------------

        state.context["is_follow_up"] = False

        state.adaptation_required = False

    # ==========================================================
    # RUN AGENT
    # ==========================================================

    orchestrator = AgentOrchestrator()

    state = orchestrator.run(state)

    # ==========================================================
    # SAVE UPDATED SESSION
    # ==========================================================

    SESSIONS[session_id] = state

    # ==========================================================
    # RESPONSE
    # ==========================================================

    return {
        "success": True,

        "session_id": session_id,

        "summary": (
            state.action_plan[0]
            if state.action_plan
            else (
                "I analyzed the available "
                "information."
            )
        ),

        "language": state.language,

        "script": state.script,

        "input_type": state.input_type,

        "intent": state.intent,

        "user_goal": state.user_goal,

        "situation": state.situation,

        "risk_score": state.risk_score,

        "risk_level": state.risk_level,

        "risk_factors": (
            state.risk_factors
        ),

        "consequences": (
            state.consequences
        ),

        "what_to_do": (
            state.what_to_do
        ),

        "what_not_to_do": (
            state.what_not_to_do
        ),

        "action_plan": (
            state.action_plan
        ),

        "important_only": (
            state.context.get(
                "important_only",
                {},
            )
        ),

        "document_insights": (
            state.context.get(
                "document_insights",
                {},
            )
        ),

        "retrieved_knowledge": (
            state.context.get(
                "retrieved_knowledge",
                [],
            )
        ),

        "agent_activity": (
            state.agent_activity
        ),

        "needs_follow_up": (
            state.needs_follow_up
        ),

        "follow_up_questions": (
            state.follow_up_questions
        ),

        "evaluation_status": (
            state.evaluation_status
        ),

        "adaptation_required": (
            state.adaptation_required
        ),

        "confidence": (
            state.confidence
        ),

        "state": state.model_dump(),
    }


# ==============================================================
# LEGACY IMAGE ENDPOINT
# ==============================================================

@app.post("/api/analyze-image")
async def analyze_image(
    file: UploadFile = File(...),
):
    """
    Backward-compatible image analysis endpoint.
    """

    file_path = save_upload(file)

    session_id = create_session()

    state = AgentState(
        session_id=session_id,
        language="English",
        input_type="image",
        input_file_path=file_path,
        messages=[
            AgentMessage(
                role="user",
                content=(
                    "Analyze the uploaded image: "
                    f"{file.filename}"
                ),
            )
        ],
    )

    state.intent = "digital_safety"

    state.user_goal = (
        "Understand the uploaded image "
        "and determine whether action is required"
    )

    orchestrator = AgentOrchestrator()

    state = orchestrator.run(state)

    SESSIONS[session_id] = state

    return {
        "success": True,
        "session_id": session_id,
        "state": state.model_dump(),
    }
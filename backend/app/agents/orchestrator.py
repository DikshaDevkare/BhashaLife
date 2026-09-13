from app.models.schemas import AgentState, ToolResult

from app.services.action_planner import build_action_plan
from app.services.bhasha_shield import detect_language
from app.services.life_shield import assess_risk
from app.services.rag import retrieve

from app.services.document_intelligence import (
    extract_document_intelligence,
)

from app.tools.document_parser import parse_document
from app.tools.ocr import extract_text_from_image
from app.tools.url_analyzer import analyze_text_for_url


class AgentOrchestrator:
    """
    Central controller for the BhashaLife AI agent.

    Agent workflow:

    Understand
        ↓
    Select Tools
        ↓
    Execute Tools
        ↓
    Assess Risk
        ↓
    Build Action Plan
        ↓
    Evaluate
        ↓
    Adapt / Replan
    """

    def __init__(self):
        self.name = "BhashaLife Agent Orchestrator"

    # ==============================================================
    # LANGUAGE PREFERENCE
    # ==============================================================

    def apply_language_preference(
        self,
        state: AgentState,
        detected_language: str,
        detected_script: str,
        detected_mode: str,
        detected_confidence: float,
    ) -> AgentState:
        """
        Apply the user's explicit language preference.

        Auto:
            use detected language + script.

        Manual language:
            keep the selected language, while preserving the user's
            comfortable script when possible.

        Hinglish / Roman:
            always use Latin/Roman output.
        """

        preference = (
            state.context.get("language_preference")
            or state.language
            or "Auto"
        )

        if preference == "Auto":
            state.language = detected_language
            state.script = detected_script
            state.context["language_mode"] = detected_mode

        elif preference == "English":
            state.language = "English"
            state.script = "Latin"
            state.context["language_mode"] = "native"

        elif preference == "Hindi":
            state.language = "Hindi"
            state.script = (
                "Latin"
                if detected_script == "Latin"
                else "Devanagari"
            )
            state.context["language_mode"] = (
                "Roman"
                if state.script == "Latin"
                else "native"
            )

        elif preference == "Marathi":
            state.language = "Marathi"
            state.script = (
                "Latin"
                if detected_script == "Latin"
                else "Devanagari"
            )
            state.context["language_mode"] = (
                "Roman"
                if state.script == "Latin"
                else "native"
            )

        elif preference == "Hinglish / Roman":
            if detected_language == "Marathi":
                state.language = "Marathi"
            elif detected_language == "Hindi":
                state.language = "Hindi"
            else:
                state.language = "Hinglish / Roman"

            state.script = "Latin"
            state.context["language_mode"] = "Roman"

        else:
            state.language = detected_language
            state.script = detected_script
            state.context["language_mode"] = detected_mode

        state.context["language_preference"] = preference
        state.context["language_confidence"] = detected_confidence

        return state

    # ==============================================================
    # UNDERSTAND
    # ==============================================================

    def understand(
        self,
        state: AgentState,
    ) -> AgentState:
        """
        Understand the user's input, language, intent,
        goal and whether this is a follow-up.
        """

        state.current_step = "understanding"

        state.agent_activity.append(
            "Understanding user input"
        )

        # ----------------------------------------------------------
        # Latest message
        # ----------------------------------------------------------

        latest_message = ""

        if state.messages:
            latest_message = (
                state.messages[-1]
                .content
                .strip()
            )

        # ----------------------------------------------------------
        # Follow-up detection
        # ----------------------------------------------------------

        is_follow_up = bool(
            state.context.get(
                "is_follow_up",
                False,
            )
        )

        # ----------------------------------------------------------
        # Bhasha Shield
        # ----------------------------------------------------------

        if latest_message:

            # Keep the incoming UI choice as the explicit preference.
            # "Auto" means the detector decides the language.
            selected_language = (
                state.language or "Auto"
            )

            state.context[
                "language_preference"
            ] = selected_language

            normalized_message = (
                latest_message
                .lower()
                .strip()
            )

            # Strong Roman-language markers for short follow-ups.
            marathi_markers = [
                "majhyakade",
                "mazyakade",
                "mazhyakade",
                "majha",
                "majhi",
                "majhe",
                "mala",
                "mi",
                "mala kay",
                "kay karu",
                "karu",
                "kela",
                "kelay",
                "pahije",
                "aahe",
                "ahe",
                "ata",
                "tumcha",
                "tumhala",
                "tumhi",
                "ghya",
                "kara",
            ]

            hindi_markers = [
                "mere paas",
                "mere pass",
                "mujhe",
                "mera",
                "meri",
                "mere",
                "mujhko",
                "kya karu",
                "karna hai",
                "karna",
                "chahiye",
                "abhi",
                "aapka",
                "aapko",
                "aap",
                "hai",
                "hain",
            ]

            marathi_score = sum(
                1
                for marker in marathi_markers
                if marker in normalized_message
            )

            hindi_score = sum(
                1
                for marker in hindi_markers
                if marker in normalized_message
            )

            if (
                marathi_score >= 1
                and (
                    "nahi" in normalized_message
                    or "nahiye" in normalized_message
                    or marathi_score >= 2
                )
            ):
                detected_language = "Marathi"
                detected_script = "Latin"
                detected_mode = "Roman"
                detected_confidence = 0.90

            elif (
                hindi_score >= 2
                and (
                    "nahi" in normalized_message
                    or hindi_score >= 3
                )
            ):
                detected_language = "Hindi"
                detected_script = "Latin"
                detected_mode = "Roman"
                detected_confidence = 0.90

            else:
                language_result = detect_language(
                    latest_message,
                    "English",
                )

                detected_language = (
                    language_result["language"]
                )
                detected_script = (
                    language_result["script"]
                )
                detected_mode = (
                    language_result["mode"]
                )
                detected_confidence = (
                    language_result["confidence"]
                )

            state = self.apply_language_preference(
                state,
                detected_language,
                detected_script,
                detected_mode,
                detected_confidence,
            )

        else:
            # Preserve the explicit preference even if there is no
            # message to detect from.
            state.context.setdefault(
                "language_preference",
                state.language or "Auto",
            )

        state.agent_activity.append(
            f"Language detected: "
            f"{state.language} "
            f"({state.script})"
        )

        # ----------------------------------------------------------
        # FOLLOW-UP REQUEST
        # ----------------------------------------------------------

        if is_follow_up:

            state.agent_activity.append(
                "Follow-up request detected"
            )

            state.agent_activity.append(
                "Preserving previous situation and goal"
            )

            # ------------------------------------------------------
            # Do NOT overwrite the previous intent.
            #
            # This is critical for adaptation.
            # ------------------------------------------------------

            if not state.intent:

                state.intent = (
                    "general_resolution"
                )

            if not state.user_goal:

                state.user_goal = (
                    "Understand the situation "
                    "and determine the best next action"
                )

            return state

        # ----------------------------------------------------------
        # IMAGE INPUT
        # ----------------------------------------------------------

        if state.input_type == "image":

            state.user_goal = (
                "Understand and analyze "
                "the uploaded image"
            )

            state.intent = (
                "image_analysis"
            )

            return state

        # ----------------------------------------------------------
        # NO MESSAGE
        # ----------------------------------------------------------

        if not state.messages:

            state.user_goal = (
                "Understand the provided situation"
            )

            state.intent = (
                "general_resolution"
            )

            return state

        # ----------------------------------------------------------
        # Detect intent
        # ----------------------------------------------------------

        latest_lower = (
            latest_message.lower()
        )

        # ----------------------------------------------------------
        # Digital safety
        # ----------------------------------------------------------

        if any(
            word in latest_lower
            for word in [
                "otp",
                "scam",
                "phishing",
                "fraud",
                "bank",
                "transaction",
                "password",
                "cvv",
                "pin",
                "account",
                "payment",
            ]
        ):

            state.intent = (
                "digital_safety"
            )

            state.user_goal = (
                "Determine whether the situation "
                "is risky and what action to take"
            )

        # ----------------------------------------------------------
        # Document guidance
        # ----------------------------------------------------------

        elif (
            state.input_type == "document"
            or any(
                word in latest_lower
                for word in [
                    "notice",
                    "form",
                    "deadline",
                    "college",
                    "document",
                    "certificate",
                    "application",
                    "submit",
                    "bonafide",
                ]
            )
        ):

            state.intent = (
                "document_guidance"
            )

            state.user_goal = (
                "Understand the document "
                "and determine the required "
                "next steps"
            )

        # ----------------------------------------------------------
        # General resolution
        # ----------------------------------------------------------

        else:

            state.intent = (
                "general_resolution"
            )

            state.user_goal = (
                "Understand the situation "
                "and determine the best next action"
            )

        return state

    # ==============================================================
    # SELECT TOOLS
    # ==============================================================

    def select_tools(
        self,
        state: AgentState,
    ) -> AgentState:
        """
        Dynamically select tools according to the situation.
        """

        state.current_step = (
            "tool_selection"
        )

        state.agent_activity.append(
            "Selecting investigation tools"
        )

        tools = []

        is_follow_up = bool(
            state.context.get(
                "is_follow_up",
                False,
            )
        )

        # ----------------------------------------------------------
        # Follow-up without a new file
        #
        # Do NOT parse the previous PDF again.
        # The previous document intelligence is already in state.
        # ----------------------------------------------------------

        if (
            is_follow_up
            and not state.context.get(
                "new_file",
                False,
            )
        ):

            # RAG can provide additional supporting knowledge.

            tools.append(
                "safety_rag"
            )

        # ----------------------------------------------------------
        # New image
        # ----------------------------------------------------------

        elif state.input_type == "image":

            tools.append(
                "ocr"
            )

        # ----------------------------------------------------------
        # Digital safety
        # ----------------------------------------------------------

        elif state.intent == "digital_safety":

            tools.extend(
                [
                    "url_analyzer",
                    "safety_rag",
                ]
            )

        # ----------------------------------------------------------
        # New document
        # ----------------------------------------------------------

        elif state.intent == "document_guidance":

            tools.extend(
                [
                    "document_parser",
                    "safety_rag",
                ]
            )

        # ----------------------------------------------------------
        # General
        # ----------------------------------------------------------

        else:

            tools.append(
                "safety_rag"
            )

        state.selected_tools = list(
            dict.fromkeys(tools)
        )

        state.agent_activity.append(
            "Selected tools: "
            + (
                ", ".join(
                    state.selected_tools
                )
                if state.selected_tools
                else "none"
            )
        )

        return state

    # ==============================================================
    # EXECUTE TOOLS
    # ==============================================================

    def execute_tools(
        self,
        state: AgentState,
    ) -> AgentState:
        """
        Execute selected tools dynamically.

        A tool can cause another tool to be selected
        based on newly discovered evidence.
        """

        state.current_step = (
            "tool_execution"
        )

        executed_tools = set()
        tool_index = 0

        while tool_index < len(
            state.selected_tools
        ):

            tool_name = (
                state.selected_tools[
                    tool_index
                ]
            )

            if tool_name in executed_tools:

                tool_index += 1
                continue

            executed_tools.add(
                tool_name
            )

            # ======================================================
            # OCR
            # ======================================================

            if tool_name == "ocr":

                state.agent_activity.append(
                    "Running OCR on uploaded image"
                )

                if not state.input_file_path:

                    result = ToolResult(
                        tool_name="ocr",
                        success=False,
                        summary=(
                            "No image path "
                            "was provided."
                        ),
                        data={},
                    )

                else:

                    ocr_result = (
                        extract_text_from_image(
                            state.input_file_path
                        )
                    )

                    result = ToolResult(
                        tool_name=(
                            ocr_result[
                                "tool_name"
                            ]
                        ),
                        success=(
                            ocr_result[
                                "success"
                            ]
                        ),
                        summary=(
                            ocr_result[
                                "summary"
                            ]
                        ),
                        data=(
                            ocr_result[
                                "data"
                            ]
                        ),
                    )

                state.tool_results.append(
                    result
                )

                if result.success:

                    extracted_text = (
                        result.data.get(
                            "text",
                            "",
                        )
                    )

                    state.context[
                        "extracted_text"
                    ] = extracted_text

                    state.agent_activity.append(
                        "OCR completed — "
                        "text extracted successfully"
                    )

                    # Bhasha Shield on OCR text

                    if extracted_text:

                        language_result = detect_language(
                            extracted_text,
                            "English",
                        )

                        state = self.apply_language_preference(
                            state,
                            language_result["language"],
                            language_result["script"],
                            language_result["mode"],
                            language_result["confidence"],
                        )

                        state.agent_activity.append(
                            "Bhasha Shield: "
                            + state.language
                            + " ("
                            + state.script
                            + ")"
                        )

                    # Dynamic safety RAG

                    lower_text = (
                        extracted_text.lower()
                    )

                    safety_keywords = [
                        "otp",
                        "pin",
                        "cvv",
                        "password",
                        "bank",
                        "account",
                        "transaction",
                        "fraud",
                        "scam",
                        "phishing",
                        "verify",
                        "urgent",
                        "payment",
                        "link",
                    ]

                    if any(
                        keyword in lower_text
                        for keyword in safety_keywords
                    ):

                        if (
                            "safety_rag"
                            not in state.selected_tools
                        ):

                            state.selected_tools.append(
                                "safety_rag"
                            )

                            state.agent_activity.append(
                                "New evidence detected — "
                                "selecting safety RAG"
                            )

                else:

                    state.agent_activity.append(
                        "OCR failed — "
                        "additional input may be required"
                    )

                tool_index += 1
                continue

            # ======================================================
            # URL ANALYZER
            # ======================================================

            if tool_name == "url_analyzer":

                state.agent_activity.append(
                    "Analyzing URL evidence"
                )

                text_for_url = ""

                if state.messages:

                    text_for_url = (
                        state.messages[-1]
                        .content
                    )

                extracted_text = (
                    state.context.get(
                        "extracted_text",
                        "",
                    )
                )

                if extracted_text:

                    text_for_url += (
                        " "
                        + extracted_text
                    )

                url_result = (
                    analyze_text_for_url(
                        text_for_url
                    )
                )

                result = ToolResult(
                    tool_name=(
                        url_result[
                            "tool_name"
                        ]
                    ),
                    success=(
                        url_result[
                            "success"
                        ]
                    ),
                    summary=(
                        url_result[
                            "summary"
                        ]
                    ),
                    data=(
                        url_result.get(
                            "data",
                            {},
                        )
                    ),
                )

                state.tool_results.append(
                    result
                )

                if result.success:

                    url_data = (
                        result.data
                    )

                    state.context[
                        "url_analysis"
                    ] = url_data

                    indicators = (
                        url_data.get(
                            "indicators",
                            [],
                        )
                    )

                    suspicious_terms = (
                        url_data.get(
                            "suspicious_terms",
                            [],
                        )
                    )

                    if indicators:

                        state.agent_activity.append(
                            "URL analysis found "
                            + str(
                                len(
                                    indicators
                                )
                            )
                            + " suspicious indicator(s)"
                        )

                    elif suspicious_terms:

                        state.agent_activity.append(
                            "URL analysis detected "
                            "suspicious URL terms"
                        )

                    else:

                        state.agent_activity.append(
                            "URL analysis completed — "
                            "no obvious structural "
                            "red flags"
                        )

                else:

                    state.agent_activity.append(
                        "URL analysis could not "
                        "be completed"
                    )

                tool_index += 1
                continue

            # ======================================================
            # SAFETY RAG
            # ======================================================

            if tool_name == "safety_rag":

                state.agent_activity.append(
                    "Retrieving trusted safety knowledge"
                )

                query_parts = []

                if state.user_goal:

                    query_parts.append(
                        state.user_goal
                    )

                if state.messages:

                    query_parts.append(
                        state.messages[-1]
                        .content
                    )

                extracted_text = (
                    state.context.get(
                        "extracted_text"
                    )
                )

                if extracted_text:

                    query_parts.append(
                        extracted_text
                    )

                # Document intelligence

                document_insights = (
                    state.context.get(
                        "document_insights"
                    )
                )

                if document_insights:

                    query_parts.extend(
                        [
                            "official document guidance",
                            "deadline",
                            "required documents",
                            "application submission",
                        ]
                    )

                    situation = (
                        document_insights.get(
                            "situation"
                        )
                    )

                    deadline = (
                        document_insights.get(
                            "deadline"
                        )
                    )

                    required_documents = (
                        document_insights.get(
                            "required_documents",
                            [],
                        )
                    )

                    action = (
                        document_insights.get(
                            "action"
                        )
                    )

                    consequence = (
                        document_insights.get(
                            "consequence"
                        )
                    )

                    if situation:
                        query_parts.append(
                            situation
                        )

                    if deadline:
                        query_parts.append(
                            deadline
                        )

                    if required_documents:
                        query_parts.extend(
                            required_documents
                        )

                    if action:
                        query_parts.append(
                            action
                        )

                    if consequence:
                        query_parts.append(
                            consequence
                        )

                # URL evidence

                url_analysis = (
                    state.context.get(
                        "url_analysis"
                    )
                )

                if url_analysis:

                    query_parts.extend(
                        url_analysis.get(
                            "indicators",
                            [],
                        )
                    )

                    query_parts.extend(
                        url_analysis.get(
                            "suspicious_terms",
                            [],
                        )
                    )

                query = " ".join(
                    query_parts
                )

                rag_result = retrieve(
                    query=query,
                    top_k=3,
                )

                result = ToolResult(
                    tool_name=(
                        rag_result[
                            "tool_name"
                        ]
                    ),
                    success=(
                        rag_result[
                            "success"
                        ]
                    ),
                    summary=(
                        rag_result[
                            "summary"
                        ]
                    ),
                    data=(
                        rag_result[
                            "data"
                        ]
                    ),
                )

                state.tool_results.append(
                    result
                )

                if result.success:

                    results = (
                        result.data.get(
                            "results",
                            [],
                        )
                    )

                    # Keep document guidance and digital-safety knowledge
                    # separated at the application layer. This prevents a
                    # college notice from inheriting banking/OTP advice.
                    if state.intent == "document_guidance":
                        document_results = [
                            item
                            for item in results
                            if "document" in str(
                                item.get("source_file", "")
                            ).lower()
                            or "notice" in str(
                                item.get("title", "")
                            ).lower()
                            or "deadline" in str(
                                item.get("title", "")
                            ).lower()
                            or "require" in str(
                                item.get("title", "")
                            ).lower()
                        ]
                        state.context[
                            "retrieved_knowledge"
                        ] = document_results
                    else:
                        state.context[
                            "retrieved_knowledge"
                        ] = results

                    state.agent_activity.append(
                        "RAG retrieved "
                        + str(
                            len(
                                state.context.get(
                                    "retrieved_knowledge",
                                    []
                                )
                            )
                        )
                        + " relevant knowledge chunks"
                    )

                else:

                    state.agent_activity.append(
                        "RAG found no relevant knowledge"
                    )

                tool_index += 1
                continue

            # ======================================================
            # DOCUMENT PARSER
            # ======================================================

            if tool_name == "document_parser":

                state.agent_activity.append(
                    "Parsing uploaded document"
                )

                if not state.input_file_path:

                    result = ToolResult(
                        tool_name=(
                            "document_parser"
                        ),
                        success=False,
                        summary=(
                            "No document path "
                            "was provided."
                        ),
                        data={},
                    )

                else:

                    parser_result = (
                        parse_document(
                            state.input_file_path
                        )
                    )

                    result = ToolResult(
                        tool_name=(
                            parser_result[
                                "tool_name"
                            ]
                        ),
                        success=(
                            parser_result[
                                "success"
                            ]
                        ),
                        summary=(
                            parser_result[
                                "summary"
                            ]
                        ),
                        data=(
                            parser_result.get(
                                "data",
                                {},
                            )
                        ),
                    )

                state.tool_results.append(
                    result
                )

                if result.success:

                    extracted_text = (
                        result.data.get(
                            "text",
                            "",
                        )
                    )

                    state.context[
                        "extracted_text"
                    ] = extracted_text

                    state.context[
                        "document_parser"
                    ] = result.data

                    state.agent_activity.append(
                        "Document parsing completed — "
                        "text extracted successfully"
                    )

                    # --------------------------------------------------
                    # Document Intelligence
                    # --------------------------------------------------

                    if extracted_text:

                        state.agent_activity.append(
                            "Extracting document intelligence"
                        )

                        intelligence_result = (
                            extract_document_intelligence(
                                extracted_text
                            )
                        )

                        if intelligence_result[
                            "success"
                        ]:

                            document_insights = (
                                intelligence_result[
                                    "data"
                                ]
                            )

                            state.context[
                                "document_insights"
                            ] = document_insights

                            if document_insights.get(
                                "situation"
                            ):

                                state.situation = (
                                    document_insights[
                                        "situation"
                                    ]
                                )

                            state.user_goal = (
                                "Understand the document "
                                "and complete the required "
                                "next steps"
                            )

                            state.agent_activity.append(
                                "Document Intelligence: "
                                "deadline, requirements, "
                                "action and consequence "
                                "extracted"
                            )

                        else:

                            state.agent_activity.append(
                                "Document Intelligence "
                                "could not extract structured "
                                "information"
                            )

                    # --------------------------------------------------
                    # Bhasha Shield
                    # --------------------------------------------------

                    if extracted_text:

                        language_result = detect_language(
                            extracted_text,
                            "English",
                        )

                        state = self.apply_language_preference(
                            state,
                            language_result["language"],
                            language_result["script"],
                            language_result["mode"],
                            language_result["confidence"],
                        )

                        state.agent_activity.append(
                            "Bhasha Shield: "
                            + state.language
                            + " ("
                            + state.script
                            + ")"
                        )

                    # --------------------------------------------------
                    # Check document URL
                    # --------------------------------------------------

                    if extracted_text:

                        url_result = (
                            analyze_text_for_url(
                                extracted_text
                            )
                        )

                        if url_result[
                            "success"
                        ]:

                            if (
                                "url_analyzer"
                                not in state.selected_tools
                            ):

                                state.selected_tools.append(
                                    "url_analyzer"
                                )

                                state.agent_activity.append(
                                    "New evidence detected — "
                                    "selecting URL Analyzer"
                                )

                else:

                    if result.data.get(
                        "needs_ocr",
                        False,
                    ):

                        state.agent_activity.append(
                            "Document contains no "
                            "readable text — OCR "
                            "may be required"
                        )

                    else:

                        state.agent_activity.append(
                            "Document parsing failed"
                        )

                tool_index += 1
                continue

            # Unknown tool

            state.agent_activity.append(
                "Unknown tool skipped: "
                + tool_name
            )

            tool_index += 1

        return state

    # ==============================================================
    # LIFE SHIELD
    # ==============================================================

    def assess_life_shield(
        self,
        state: AgentState,
    ) -> AgentState:
        """
        Convert collected evidence into risk intelligence.
        """

        state.current_step = (
            "risk_assessment"
        )

        state.agent_activity.append(
            "Evaluating risk and potential consequences"
        )

        text_parts = []

        # User messages

        for message in state.messages:

            text_parts.append(
                message.content
            )

        # Extracted document/image text

        extracted_text = (
            state.context.get(
                "extracted_text"
            )
        )

        if extracted_text:

            text_parts.append(
                extracted_text
            )

        # Document intelligence

        document_insights = (
            state.context.get(
                "document_insights"
            )
        )

        if document_insights:

            for key in [
                "situation",
                "deadline",
                "action",
                "consequence",
            ]:

                value = (
                    document_insights.get(
                        key
                    )
                )

                if value:

                    text_parts.append(
                        str(value)
                    )

            required_documents = (
                document_insights.get(
                    "required_documents",
                    [],
                )
            )

            text_parts.extend(
                required_documents
            )

        combined_text = " ".join(
            text_parts
        )

        # URL evidence

        url_analysis = (
            state.context.get(
                "url_analysis",
                {},
            )
        )

        if url_analysis:

            indicators = (
                url_analysis.get(
                    "indicators",
                    [],
                )
            )

            suspicious_terms = (
                url_analysis.get(
                    "suspicious_terms",
                    [],
                )
            )

            combined_text += (
                " "
                + " ".join(
                    indicators
                )
            )

            combined_text += (
                " "
                + " ".join(
                    suspicious_terms
                )
            )

        # RAG evidence

        retrieved_knowledge = (
            state.context.get(
                "retrieved_knowledge",
                [],
            )
        )

        risk_result = assess_risk(
            text=combined_text,
            rag_results=retrieved_knowledge,
            intent=state.intent,
            url_analysis=url_analysis,
            document_insights=document_insights or {},
        )

        state.risk_score = (
            risk_result[
                "risk_score"
            ]
        )

        state.risk_level = (
            risk_result[
                "risk_level"
            ]
        )

        state.risk_factors = (
            risk_result[
                "risk_factors"
            ]
        )

        state.consequences = (
            risk_result[
                "consequences"
            ]
        )

        state.what_to_do = (
            risk_result.get(
                "what_to_do",
                [],
            )
        )

        state.what_not_to_do = (
            risk_result.get(
                "what_not_to_do",
                [],
            )
        )

        state.things_to_avoid = (
            state.what_not_to_do
        )

        state.confidence = (
            risk_result[
                "confidence"
            ]
        )

        state.context[
            "life_shield"
        ] = risk_result

        state.agent_activity.append(
            "Risk assessed: "
            + state.risk_level
            + " ("
            + str(
                state.risk_score
            )
            + "/100)"
        )

        return state

    # ==============================================================
    # ACTION PLAN
    # ==============================================================

    def build_action_plan(
        self,
        state: AgentState,
    ) -> AgentState:
        """
        Generate an actionable plan.
        """

        state.current_step = (
            "action_planning"
        )

        state.agent_activity.append(
            "Building personalized action plan"
        )

        plan = build_action_plan(
            risk_level=state.risk_level,
            risk_factors=state.risk_factors,
            consequences=state.consequences,
            what_to_do=state.what_to_do,
            what_not_to_do=state.what_not_to_do,
        )

        state.action_plan = (
            plan["actions"]
        )

        state.what_to_do = (
            plan["what_to_do"]
        )

        state.what_not_to_do = (
            plan["what_not_to_do"]
        )

        state.things_to_avoid = (
            state.what_not_to_do
        )

        state.context[
            "important_only"
        ] = plan[
            "important_only"
        ]

        # ----------------------------------------------------------
        # Add document information to Important Only
        # ----------------------------------------------------------

        document_insights = (
            state.context.get(
                "document_insights"
            )
        )

        if document_insights:

            important_only = (
                state.context.get(
                    "important_only",
                    {},
                )
            )

            important_only[
                "situation"
            ] = document_insights.get(
                "situation"
            )

            important_only[
                "deadline"
            ] = document_insights.get(
                "deadline"
            )

            important_only[
                "required_documents"
            ] = document_insights.get(
                "required_documents",
                [],
            )

            important_only[
                "action"
            ] = document_insights.get(
                "action"
            )

            important_only[
                "consequence"
            ] = document_insights.get(
                "consequence"
            )

            state.context[
                "important_only"
            ] = important_only

        state.agent_activity.append(
            "Action plan generated with "
            + str(
                len(
                    state.action_plan
                )
            )
            + " step(s)"
        )

        return state

    # ==============================================================
    # EVALUATE
    # ==============================================================

    def evaluate(
        self,
        state: AgentState,
    ) -> AgentState:
        """
        Evaluate whether enough evidence exists and whether
        new information requires adaptation.
        """

        state.current_step = (
            "evaluation"
        )

        state.agent_activity.append(
            "Evaluating investigation result"
        )

        successful_results = [
            result
            for result in state.tool_results
            if result.success
        ]

        has_document_intelligence = bool(
            state.context.get(
                "document_insights"
            )
        )

        has_risk_result = (
            "life_shield"
            in state.context
        )

        has_action_plan = bool(
            state.action_plan
        )

        # ----------------------------------------------------------
        # No successful tool
        # ----------------------------------------------------------

        if not successful_results:

            state.evaluation_status = (
                "incomplete"
            )

            state.adaptation_required = True

            state.agent_activity.append(
                "Investigation incomplete — "
                "replanning required"
            )

            return state

        # ----------------------------------------------------------
        # Document intelligence check
        # ----------------------------------------------------------

        if (
            state.intent
            == "document_guidance"
            and not has_document_intelligence
        ):

            state.evaluation_status = (
                "incomplete"
            )

            state.adaptation_required = True

            state.agent_activity.append(
                "Document understanding incomplete — "
                "replanning required"
            )

            return state

        # ----------------------------------------------------------
        # Risk check
        # ----------------------------------------------------------

        if not has_risk_result:

            state.evaluation_status = (
                "incomplete"
            )

            state.adaptation_required = True

            state.agent_activity.append(
                "Risk evaluation incomplete — "
                "replanning required"
            )

            return state

        # ----------------------------------------------------------
        # Action plan check
        # ----------------------------------------------------------

        if not has_action_plan:

            state.evaluation_status = (
                "incomplete"
            )

            state.adaptation_required = True

            state.agent_activity.append(
                "Action plan incomplete — "
                "replanning required"
            )

            return state

        # ----------------------------------------------------------
        # FOLLOW-UP / NEW INFORMATION
        # ----------------------------------------------------------

        is_follow_up = bool(
            state.context.get(
                "is_follow_up",
                False,
            )
        )

        if is_follow_up:

            latest_message = ""

            if state.messages:

                latest_message = (
                    state.messages[-1]
                    .content
                    .strip()
                    .lower()
                )

            missing_document_terms = [
                "bonafide",
                "bonafide certificate",
                "student id",
                "student id nahi",
                "photo",
                "photograph",
                "document",
            ]

            missing_words = [
                "nahi",
                "nahi hai",
                "don't have",
                "do not have",
                "not have",
                "missing",
            ]

            has_missing_language = any(
                word in latest_message
                for word in missing_words
            )

            has_document_reference = any(
                term in latest_message
                for term in missing_document_terms
            )

            if (
                has_missing_language
                and has_document_reference
            ):

                state.evaluation_status = (
                    "adaptation_required"
                )

                state.adaptation_required = True

                state.agent_activity.append(
                    "New information changes the "
                    "current situation"
                )

                state.agent_activity.append(
                    "Missing requirement detected"
                )

                return state

            # Generic follow-up

            state.evaluation_status = (
                "adaptation_required"
            )

            state.adaptation_required = True

            state.agent_activity.append(
                "New follow-up information detected"
            )

            return state

        # ----------------------------------------------------------
        # Normal successful investigation
        # ----------------------------------------------------------

        state.evaluation_status = (
            "success"
        )

        state.adaptation_required = False

        state.agent_activity.append(
            "Investigation result verified"
        )

        return state

    # ==============================================================
    # ADAPT
    # ==============================================================

    def adapt(
        self,
        state: AgentState,
    ) -> AgentState:
        """
         Adapt and replan when new user information changes
        the current situation.
        """

        state.current_step = "adaptation"

        if not state.adaptation_required:
            return state

        state.agent_activity.append(
            "Replanning based on new information"
        )

        # ----------------------------------------------------------
        # Recover previous context
        # ----------------------------------------------------------

        previous_state = state.previous_state or {}

        previous_context = (
            previous_state.get("context", {})
            if isinstance(previous_state, dict)
            else {}
        )

        document_insights = (
            state.context.get("document_insights")
            or previous_context.get("document_insights")
            or {}
        )

        latest_message = ""

        if state.messages:
            latest_message = (
                state.messages[-1].content.strip()
            )

        latest_lower = latest_message.lower()

        # ----------------------------------------------------------
        # Save latest information
        # ----------------------------------------------------------

        state.context["latest_follow_up"] = latest_message

        # ----------------------------------------------------------
        # Detect whether user says something is unavailable
        # ----------------------------------------------------------

        missing_phrases = [
            "don't have",
            "do not have",
            "not have",
            "i dont have",
            "i don't have",
            "i do not have",
            "missing",
            "not available",
            "unavailable",
            "cannot provide",
            "can't provide",
            "cant provide",
            "nahi hai",
            "nahi hain",
            "nahi",
            "mere paas nahi",
            "mere pass nahi",
            "mazya kade nahi",
            "mazyakade nahi",
            "majhyakade nahi",
            "mala nahi",
        ]

        has_missing_language = (
            any(
                phrase in latest_lower
                for phrase in [
                    "don't have",
                    "do not have",
                    "not have",
                    "missing",
                    "not available",
                    "unavailable",
                    "nahi",
                    "nahi hai",
                    "nahi hain",
                    "nahiye",
                ]
            )
            or (
                any(
                    phrase in latest_lower
                    for phrase in [
                        "majhyakade",
                        "mazyakade",
                        "mazhyakade",
                        "mala",
                        "mere paas",
                        "mere pass",
                    ]
                )
                and "nahi" in latest_lower
            )
        )
        # ----------------------------------------------------------
        # Find matching required document dynamically
        # ----------------------------------------------------------

        required_documents = document_insights.get(
            "required_documents",
            []
        )

        missing_document = None

        def normalize(value):
            value = str(value).lower()

            replacements = {
                "identity card": "id",
                "college identity card": "college id",
                "student identity card": "student id",
                "id card": "id",
                "passport size photo": "photo",
                "passport photograph": "photo",
                "photograph": "photo",
                "recent photograph": "photo",
            }

            for old, new in replacements.items():
                value = value.replace(old, new)

            return value

        message_normalized = normalize(latest_lower)

        # Direct / semantic matching against requirements
        for requirement in required_documents:

            if not requirement:
                continue

            req = normalize(requirement)

            req_words = {
                word
                for word in req.replace("-", " ").split()
                if len(word) > 2
            }

            message_words = {
                word
                for word in message_normalized.replace("-", " ").split()
                if len(word) > 2
            }

            overlap = req_words.intersection(message_words)

            # Strong direct match
            if req in message_normalized:
                missing_document = requirement
                break

            # Handle cases like:
            # "College ID" vs "college identity card"
            if (
                "id" in req_words
                and (
                    "id" in message_words
                    or "identity" in message_words
                    or "card" in message_words
                )
                and overlap
            ):
                missing_document = requirement
                break

            # General semantic overlap
            if len(overlap) >= 1 and has_missing_language:
                missing_document = requirement
                break

        # ----------------------------------------------------------
        # Common aliases when requirement wording differs
        # ----------------------------------------------------------

        if not missing_document and has_missing_language:

            alias_groups = {
                "id": [
                    "id",
                    "identity",
                    "identity card",
                    "college id",
                    "college identity card",
                    "student id",
                    "student identity card",
                ],
                "photo": [
                    "photo",
                    "photograph",
                    "picture",
                ],
                "bonafide": [
                    "bonafide",
                    "bonafide certificate",
                ],
            }

            for requirement in required_documents:

                req_lower = str(requirement).lower()

                for aliases in alias_groups.values():

                    if any(
                        alias in req_lower
                        for alias in aliases
                    ):

                        if any(
                            alias in latest_lower
                            for alias in aliases
                        ):
                            missing_document = requirement
                            break

                if missing_document:
                    break

        # ----------------------------------------------------------
        # ADAPTATION: Missing requirement found
        # ----------------------------------------------------------

        if missing_document:

            state.agent_activity.append(
                "Missing requirement detected: "
                + str(missing_document)
            )

            state.agent_activity.append(
                "Missing requirement confirmed: "
                + str(missing_document)
            )

            # ------------------------------------------------------
            # Update goal
            # ------------------------------------------------------

            state.user_goal = (
                "Resolve the missing "
                + str(missing_document)
                + " requirement and complete "
                "the required submission"
            )

            state.agent_activity.append(
                "Goal updated"
            )

            # ------------------------------------------------------
            # Build new adaptive plan
            # ------------------------------------------------------

            updated_plan = []

            updated_plan.append(
                "Obtain "
                + str(missing_document)
                + "."
            )

            for requirement in required_documents:

                if not requirement:
                    continue

                if (
                    str(requirement).lower()
                    != str(missing_document).lower()
                ):

                    action = (
                        "Prepare "
                        + str(requirement)
                        + "."
                    )

                    if action not in updated_plan:
                        updated_plan.append(action)

            original_action = document_insights.get(
                "action"
            )

            if original_action:
                if original_action not in updated_plan:
                    updated_plan.append(
                        original_action
                    )

            deadline = document_insights.get(
                "deadline"
            )

            if deadline:
                deadline_action = (
                    "Complete the submission before "
                    + str(deadline)
                    + "."
                )

                if deadline_action not in updated_plan:
                    updated_plan.append(
                        deadline_action
                    )

            state.action_plan = updated_plan[:5]

            state.what_to_do = list(
                state.action_plan
            )

            # ------------------------------------------------------
            # Update Important Only
            # ------------------------------------------------------

            important_only = {
                "situation": document_insights.get(
                    "situation",
                    state.situation
                ),
                "risk": state.risk_level,
                "deadline": deadline,
                "required_documents": required_documents,
                "missing_requirement": missing_document,
                "action": (
                    state.action_plan[0]
                    if state.action_plan
                    else (
                        "Obtain "
                        + str(missing_document)
                        + "."
                    )
                ),
                "consequence": document_insights.get(
                    "consequence",
                    "The missing requirement may prevent "
                    "or delay completion."
                ),
                "next_step": (
                    state.action_plan[0]
                    if state.action_plan
                    else (
                        "Obtain "
                        + str(missing_document)
                        + "."
                    )
                ),
            }

            state.context["important_only"] = (
                important_only
            )

            # ------------------------------------------------------
            # Update document intelligence
            # ------------------------------------------------------

            updated_document_insights = dict(
                document_insights
            )

            updated_document_insights[
                "missing_requirement"
            ] = missing_document

            updated_document_insights[
                "action_plan"
            ] = state.action_plan

            state.context[
                "document_insights"
            ] = updated_document_insights

            # ------------------------------------------------------
            # Agent activity
            # ------------------------------------------------------

            state.agent_activity.append(
                "Replanning actions"
            )

            state.agent_activity.append(
                "Updated action plan generated"
            )

            state.agent_activity.append(
                "Adaptive plan verified"
            )

            state.adaptation_required = False

            state.evaluation_status = "adapted"

            state.current_step = "completed"

            return state

        # ==========================================================
        # GENERIC ADAPTATION
        # ==========================================================

        state.agent_activity.append(
            "New information requires plan reassessment"
        )

        # Use the new information to create a concrete
        # next step instead of simply storing it.

        if latest_message:

            state.action_plan = [
                "Review the new information: "
                + latest_message,
                "Verify the relevant requirement or condition "
                "before proceeding.",
            ]

            state.what_to_do = list(
                state.action_plan
            )

            state.context["important_only"] = {
                "situation": state.situation,
                "risk": state.risk_level,
                "action": state.action_plan[0],
                "consequence": (
                    "The new information may change "
                    "the required next step."
                ),
                "next_step": state.action_plan[0],
            }

        state.agent_activity.append(
            "Updated action plan generated"
        )

        state.agent_activity.append(
            "Adaptive plan verified"
        )

        state.adaptation_required = False

        state.evaluation_status = "adapted"

        state.current_step = "completed"

        return state

    # ==============================================================
    # RUN
    # ==============================================================

    def run(
        self,
        state: AgentState,
    ) -> AgentState:
        """
        Execute the complete BhashaLife AI agent loop.
        """

        state = self.understand(
            state
        )

        state = self.select_tools(
            state
        )

        state = self.execute_tools(
            state
        )

        state = self.assess_life_shield(
            state
        )

        state = self.build_action_plan(
            state
        )

        state = self.evaluate(
            state
        )

        if state.adaptation_required:

            state = self.adapt(
                state
            )

        return state
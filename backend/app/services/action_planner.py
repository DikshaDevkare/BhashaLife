from typing import Any, Dict, List


def build_action_plan(
    risk_level: str,
    risk_factors: List[str],
    consequences: List[str],
    what_to_do: List[str],
    what_not_to_do: List[str],
) -> Dict[str, Any]:
    """Create a short, situation-aware action plan."""
    actions = list(dict.fromkeys(what_to_do or []))
    avoid_actions = list(dict.fromkeys(what_not_to_do or []))

    if risk_level == "CRITICAL":
        priority_action = "Stop the risky action and secure the situation immediately."
    elif risk_level == "HIGH":
        priority_action = "Pause the requested action and verify the situation through a trusted channel."
    elif risk_level == "MODERATE":
        priority_action = "Verify the important details before proceeding."
    elif risk_level == "LOW":
        priority_action = "Review the available information and complete the relevant next step."
    else:
        priority_action = "Gather enough information before taking a consequential action."

    if priority_action not in actions:
        actions.insert(0, priority_action)

    actions = list(dict.fromkeys(actions))[:5]
    next_action = actions[0] if actions else priority_action

    important_only = {
        "risk": risk_level,
        "action": next_action,
        "consequence": (
            consequences[0]
            if consequences
            else "No specific consequence was established from the available information."
        ),
        "next_step": (
            actions[1]
            if len(actions) > 1
            else next_action
        ),
    }

    return {
        "actions": actions,
        "what_to_do": actions,
        "what_not_to_do": avoid_actions,
        "important_only": important_only,
        "risk_level": risk_level,
        "risk_factors": risk_factors,
        "consequences": consequences,
    }

from enum import Enum


class SafetyCategory(str, Enum):
    NORMAL = "normal"
    SELF_HARM = "self_harm"
    MEDICATION = "medication"
    DIAGNOSIS = "diagnosis"
    EMERGENCY = "emergency"


SELF_HARM_KEYWORDS = [
    "kill myself",
    "suicide",
    "end my life",
    "hurt myself",
    "self harm",
    "don't want to live",
    "do not want to live"
]

MEDICATION_KEYWORDS = [
    "what medicine should i take",
    "which medicine should i take",
    "give me medicine",
    "prescribe",
    "what tablet should i take"
]

DIAGNOSIS_KEYWORDS = [
    "do i have depression",
    "do i have anxiety",
    "am i depressed",
    "diagnose me"
]

EMERGENCY_KEYWORDS = [
    "emergency",
    "right now in danger",
    "someone is hurting me"
]


SMALLTALK_EXACT = {
    "hi", "hello", "hey", "yo", "sup", "hiya",
    "thanks", "thank you", "ty", "thx",
    "bye", "goodbye", "see you", "cya",
    "ok", "okay", "cool", "nice", "great", "awesome",
    "good morning", "good afternoon", "good evening", "good night",
    "how are you", "how's it going", "whats up", "what's up",
    "who are you", "what are you", "what can you do"
}


def is_smalltalk(text: str) -> bool:

    stripped = text.lower().strip().rstrip("!.?,")
    return stripped in SMALLTALK_EXACT


def smalltalk_reply(text: str) -> str:

    stripped = text.lower().strip().rstrip("!.?,")

    if stripped in {"thanks", "thank you", "ty", "thx"}:
        return "You're welcome. Here whenever you need."

    if stripped in {"bye", "goodbye", "see you", "cya"}:
        return "Take care."

    if stripped in {"ok", "okay", "cool", "nice", "great", "awesome"}:
        return "Anything else you'd like to talk about?"

    if stripped in {"how are you", "how's it going", "whats up", "what's up"}:
        return "I'm here and ready to help. How are you feeling today?"

    if stripped in {"who are you", "what are you", "what can you do"}:
        return (
            "I'm WellMind, a mental wellness assistant. "
            "Ask me about stress, anxiety, sleep, or everyday wellness practices."
        )

    return "Hi, I'm WellMind. How can I support you today?"


def classify_safety(text: str) -> SafetyCategory:

    lower_text = text.lower()

    for keyword in SELF_HARM_KEYWORDS:
        if keyword in lower_text:
            return SafetyCategory.SELF_HARM

    for keyword in EMERGENCY_KEYWORDS:
        if keyword in lower_text:
            return SafetyCategory.EMERGENCY

    for keyword in MEDICATION_KEYWORDS:
        if keyword in lower_text:
            return SafetyCategory.MEDICATION

    for keyword in DIAGNOSIS_KEYWORDS:
        if keyword in lower_text:
            return SafetyCategory.DIAGNOSIS

    return SafetyCategory.NORMAL


def get_safety_response(
    category: SafetyCategory
) -> str | None:

    if category == SafetyCategory.SELF_HARM:
        return (
            "I'm concerned about what you've shared. "
            "If you might hurt yourself or cannot stay safe, "
            "please contact local emergency services or a crisis support service now. "
            "If possible, stay with someone you trust and tell them what is happening."
        )

    if category == SafetyCategory.EMERGENCY:
        return (
            "This sounds like an immediate safety situation. "
            "Please contact local emergency services or someone you trust nearby now."
        )

    if category == SafetyCategory.MEDICATION:
        return (
            "I can provide general educational information, "
            "but I can't recommend or prescribe medication. "
            "Please discuss medication with a qualified doctor or mental health professional."
        )

    if category == SafetyCategory.DIAGNOSIS:
        return (
            "I can help you understand general mental wellness information, "
            "but I can't diagnose a mental health condition. "
            "A qualified mental health professional can assess your symptoms properly."
        )

    return None

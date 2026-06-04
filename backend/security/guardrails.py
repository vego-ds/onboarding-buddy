from dataclasses import dataclass
import html
import re


SENSITIVE_PROMPT_PATTERNS = [
    r"system\s+prompt",
    r"developer\s+message",
    r"hidden\s+instruction",
    r"ignore\s+(all\s+)?previous\s+instructions",
    r"reveal\s+(your\s+)?instructions",
    r"print\s+(your\s+)?prompt",
]

PROMPT_INJECTION_PATTERNS = [
    r"ignore\s+(all\s+)?previous\s+instructions",
    r"disregard\s+(the\s+)?(above|previous)",
    r"act\s+as\s+(a\s+)?system",
    r"you\s+are\s+now",
    r"developer\s+mode",
    r"jailbreak",
    r"exfiltrate",
    r"run\s+shell",
    r"execute\s+code",
    r"drop\s+table",
]

PII_PATTERNS = [
    re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.IGNORECASE),
    re.compile(r"\b(?:\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b"),
    re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),  # US SSN
    re.compile(r"\b(?:\d[ -]*?){13,16}\b"),  # payment-card-like sequence
]


@dataclass
class SafetyDecision:
    allowed: bool
    reason: str = ""
    classifier: str = "local_llama_guard_compatible"


def classify_input_safety(text):
    """Fast local stand-in for a Llama Guard style pre-planner safety check."""
    normalized = str(text or "").lower()
    if len(normalized) > 4000:
        return SafetyDecision(False, "Input is too long for the assistant safety boundary.")

    for pattern in PROMPT_INJECTION_PATTERNS:
        if re.search(pattern, normalized):
            return SafetyDecision(
                False,
                "Input appears to contain prompt-injection or unsafe execution instructions.",
            )

    return SafetyDecision(True)


def wrap_untrusted_xml(tag_name, text):
    escaped = html.escape(str(text or ""), quote=False)
    return (
        f"<{tag_name} trust=\"untrusted\">\n"
        f"{escaped}\n"
        f"</{tag_name}>"
    )


def build_isolated_context_xml(sections, employee_context_summary=""):
    source_blocks = []
    for index, section in enumerate(sections, start=1):
        source_blocks.append(
            "\n".join(
                [
                    f'<source index="{index}" trust="untrusted">',
                    f"<title>{html.escape(section['title'], quote=False)}</title>",
                    f"<file>{html.escape(section['source'], quote=False)}</file>",
                    wrap_untrusted_xml("content", section["content"]),
                    "</source>",
                ]
            )
        )

    workflow_context = (
        wrap_untrusted_xml("workflow_context", employee_context_summary)
        if employee_context_summary
        else '<workflow_context trust="untrusted"></workflow_context>'
    )

    return "\n".join(
        [
            "<isolated_untrusted_context>",
            *source_blocks,
            workflow_context,
            "</isolated_untrusted_context>",
        ]
    )


def inspect_output_safety(answer):
    normalized = str(answer or "").lower()
    for pattern in SENSITIVE_PROMPT_PATTERNS:
        if re.search(pattern, normalized):
            return SafetyDecision(
                False,
                "Response appears to reference hidden instructions or prompt material.",
            )

    for pattern in PII_PATTERNS:
        if pattern.search(str(answer or "")):
            return SafetyDecision(False, "Response appears to contain sensitive PII.")

    return SafetyDecision(True)


def safe_output_replacement():
    return (
        "I cannot provide that response because it may expose sensitive information "
        "or hidden system instructions. Please ask HR Operations for a safe summary."
    )

from pathlib import Path


SKILL_DIR = Path(__file__).resolve().parent
PROMPT_FILE = SKILL_DIR / "prompt.txt"


def get_bazi_expert_prompt() -> str:
    """Load expert bazi prompt template from local skill folder."""
    try:
        return PROMPT_FILE.read_text(encoding="utf-8").strip()
    except Exception:
        return ""

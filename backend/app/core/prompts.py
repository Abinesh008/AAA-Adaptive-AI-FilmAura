import os
from typing import Dict
from app.core.logging import get_logger

logger = get_logger("app.prompts")

class PromptManager:
    """
    Manages loading, parsing, and interpolating prompt templates from file or fallbacks.
    """
    def __init__(self, prompts_dir: str | None = None):
        if not prompts_dir:
            # backend/app/core/prompts.py -> app/core -> app -> backend -> root / prompts
            self.prompts_dir = os.path.abspath(
                os.path.join(
                    os.path.dirname(os.path.abspath(__file__)),
                    "..", "..", "..", "prompts"
                )
            )
        else:
            self.prompts_dir = prompts_dir
            
        # Ensure the directory exists
        os.makedirs(self.prompts_dir, exist_ok=True)
            
        # Standard fallback prompts to ensure out-of-the-box operation
        self._fallbacks: Dict[str, str] = {
            "movie_identification": (
                "You are an expert movie identification agent. Identify the movie based on the user's description.\n"
                "User description: {user_description}\n"
                "Contextual hints: {context_hints}\n"
                "Response: "
            ),
            "taste_analysis": (
                "Analyze the user's cinematic taste and viewing psychology based on these movies they like.\n"
                "Favorite Movies: {favorite_movies}\n"
                "Taste Profile: "
            )
        }

    def get_prompt(self, template_name: str, **variables) -> str:
        """
        Retrieves a template by name, formats it with the provided variables, and returns it.
        """
        template_text = self._load_template_text(template_name)
        
        try:
            return template_text.format(**variables)
        except KeyError as e:
            logger.error(f"Missing variable interpolation for prompt template '{template_name}': {e}")
            raise ValueError(f"Missing required key {e} for prompt template '{template_name}'")

    def _load_template_text(self, template_name: str) -> str:
        # Check files under prompts directory (with .txt or .md extensions)
        for ext in (".txt", ".md"):
            prompt_path = os.path.join(self.prompts_dir, f"{template_name}{ext}")
            if os.path.isfile(prompt_path):
                try:
                    with open(prompt_path, "r", encoding="utf-8") as f:
                        content = f.read().strip()
                        if content:
                            logger.debug(f"Loaded prompt template '{template_name}' from {prompt_path}")
                            return content
                except Exception as e:
                    logger.warning(f"Failed to read prompt file {prompt_path}: {e}")

        # Fallback to in-code templates
        fallback = self._fallbacks.get(template_name)
        if not fallback:
            raise ValueError(f"Prompt template '{template_name}' not found on disk and no fallback exists.")
        
        logger.debug(f"Using fallback prompt template for '{template_name}'")
        return fallback

prompt_manager = PromptManager()

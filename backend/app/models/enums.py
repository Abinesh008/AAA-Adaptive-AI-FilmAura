import enum

class MovieStatus(str, enum.Enum):
    """Status stages of a movie lifecycle."""
    RELEASED = "Released"
    POST_PRODUCTION = "Post Production"
    IN_PRODUCTION = "In Production"
    CANCELED = "Canceled"
    RUMORED = "Rumored"
    PLANNED = "Planned"

class ImportanceType(str, enum.Enum):
    """Categorized importance weight for scenes or cast roles."""
    MAIN = "main"
    SUPPORTING = "supporting"
    CAMEO = "cameo"

class RelationType(str, enum.Enum):
    """Type of cinematic connection between two movies."""
    SEQUEL = "sequel"
    PREQUEL = "prequel"
    REMAKE = "remake"
    SPINOFF = "spinoff"

class InteractionType(str, enum.Enum):
    """Type of action recorded on a movie by a user."""
    RATING = "rating"
    CLICK = "click"
    SKIP = "skip"
    BOOKMARK = "bookmark"

class MusicType(str, enum.Enum):
    """Categorization of a music track inside a movie."""
    SOUNDTRACK = "soundtrack"
    SCORE = "score"
    THEME = "theme"

class CueType(str, enum.Enum):
    """Visual style classification category."""
    PALETTE = "palette"
    STYLE = "style"
    CAMERA = "camera"
    LIGHTING = "lighting"
    MOTIF = "motif"

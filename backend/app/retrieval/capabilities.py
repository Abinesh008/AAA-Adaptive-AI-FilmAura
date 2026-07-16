from typing import Dict
from app.retrieval.registry import capability_registry

def get_capability_matrix() -> Dict[str, Dict[str, bool]]:
    """
    Exposes the dynamically generated plugin capability matrix.
    """
    matrix = {}
    manifests = capability_registry.get_all_manifests()
    for name, data in manifests.items():
        matrix[name] = data.get("capabilities", {})
    return matrix

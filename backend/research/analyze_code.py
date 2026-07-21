import os
import ast

FILES_TO_ANALYZE = [
    "app/retrieval/sdk.py",
    "app/retrieval/orchestrator.py",
    "app/retrieval/planner.py",
    "app/retrieval/supervisor.py",
    "app/retrieval/registry.py",
    "app/retrieval/fusion.py",
    "app/retrieval/reranker.py",
    "app/retrieval/context_builder.py",
    "app/retrieval/reasoning.py",
    "app/retrieval/confidence.py",
    "app/retrieval/explanation.py",
    "app/retrieval/retrieval_cache.py",
]

def analyze_file(filepath):
    abs_path = os.path.join("c:/Users/USER/Documents/AAA-Adaptive-AI-FilmAura/backend", filepath)
    if not os.path.exists(abs_path):
        return {"exists": False}
        
    with open(abs_path, "r", encoding="utf-8") as f:
        content = f.read()
        
    lines = content.splitlines()
    loc = len(lines)
    
    # Parse AST
    try:
        tree = ast.parse(content)
        classes = sum(1 for node in ast.walk(tree) if isinstance(node, ast.ClassDef))
        functions = sum(1 for node in ast.walk(tree) if isinstance(node, ast.FunctionDef))
    except Exception as e:
        classes = "Error"
        functions = "Error"
        
    # Search keywords
    has_todo = "TODO" in content
    has_pass = "pass" in content
    has_not_impl = "NotImplementedError" in content
    has_placeholder = "placeholder" in content.lower()
    
    return {
        "exists": True,
        "loc": loc,
        "classes": classes,
        "functions": functions,
        "has_todo": has_todo,
        "has_pass": has_pass,
        "has_not_impl": has_not_impl,
        "has_placeholder": has_placeholder
    }

print("="*80)
print(f"{'File':<30} | {'LOC':<4} | {'Class':<5} | {'Func':<5} | {'TODO':<4} | {'pass':<4} | {'NotImpl':<7} | {'Placeh.':<7}")
print("="*80)

for f in FILES_TO_ANALYZE:
    res = analyze_file(f)
    if not res["exists"]:
        print(f"{f:<30} | DOES NOT EXIST")
    else:
        print(f"{f:<30} | {res['loc']:<4} | {res['classes']:<5} | {res['functions']:<5} | {res['has_todo']:<4} | {res['has_pass']:<4} | {res['has_not_impl']:<7} | {res['has_placeholder']:<7}")

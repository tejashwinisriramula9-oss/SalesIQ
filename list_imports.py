from pathlib import Path
import ast
root = Path('.')
imports = set()
for p in root.rglob('*.py'):
    if any(part.startswith('.') or part == 'venv' or part == '.venv' for part in p.parts):
        continue
    try:
        text = p.read_text(encoding='utf-8')
        tree = ast.parse(text)
    except Exception:
        continue
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for n in node.names:
                imports.add(n.name.split('.')[0])
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.add(node.module.split('.')[0])
for name in sorted(imports):
    print(name)

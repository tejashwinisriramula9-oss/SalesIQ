from pathlib import Path
import ast
root = Path('.')
imports = set()
for p in root.rglob('*.py'):
    if p.name == 'extract_imports.py':
        continue
    try:
        tree = ast.parse(p.read_text(encoding='utf-8'))
    except Exception as e:
        print(f'# SKIP {p}: {e}')
        continue
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for n in node.names:
                imports.add(n.name.split('.')[0])
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.add(node.module.split('.')[0])
for name in sorted(imports):
    print(name)

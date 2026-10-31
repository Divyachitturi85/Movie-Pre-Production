import os

frontend_dir = 'frontend/src'
for root, dirs, files in os.walk(frontend_dir):
    for f in files:
        if f.endswith(('.jsx', '.js', '.tsx', '.ts')):
            path = os.path.join(root, f)
            with open(path, 'r', encoding='utf-8') as file:
                lines = file.readlines()
                for i, line in enumerate(lines):
                    if 'DollarSign' in line or 'currency' in line.lower() or ('$' in line and '{' not in line and not line.strip().startswith('import') and not line.strip().startswith('//')):
                        print(f"{path}:{i+1}: {line.strip()[:80]}")

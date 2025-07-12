#!/usr/bin/env python3
"""
Import-Cleaner Script für das Backend
Entfernt ungenutzte Imports und organisiert Import-Statements
"""

import os
import ast
from pathlib import Path

def find_unused_imports(tree: ast.AST) -> List[str]:
    """Findet ungenutzte Imports"""
    import_names = set()
    used_names = set()
    
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                import_names.add(alias.asname or alias.name)
        elif isinstance(node, ast.ImportFrom):
            for alias in node.names:
                import_names.add(alias.asname or alias.name)
        elif isinstance(node, ast.Name):
            used_names.add(node.id)
        elif isinstance(node, ast.Attribute):
            if isinstance(node.value, ast.Name):
                used_names.add(node.value.id)
    
    return list(import_names - used_names)

def clean_file_imports(file_path: str) -> Dict[str, List[str]]:
    """Räumt Imports in einer Datei auf"""
    results = {
        "removed": [],
        "errors": []
    }
    
    try:
        file_path = Path(file_path)
        if not file_path.exists():
            results["errors"].append(f"Datei nicht gefunden: {file_path}")
            return results
        
        # Datei lesen
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # AST-Parsing
        tree = ast.parse(content)
        
        # Ungenutzte Imports finden
        unused_imports = find_unused_imports(tree)
        
        if unused_imports:
            # Import-Zeilen entfernen
            lines = content.split('\n')
            lines_to_remove = []
            
            for i, line in enumerate(lines):
                line_stripped = line.strip()
                
                # Import-Zeilen identifizieren
                if line_stripped.startswith(('import ', 'from ')):
                    # Prüfen ob dieser Import ungenutzt ist
                    for unused in unused_imports:
                        if unused in line_stripped:
                            lines_to_remove.append(i)
                            break
            
            # Zeilen entfernen (rückwärts um Indizes nicht zu verschieben)
            for i in reversed(lines_to_remove):
                del lines[i]
            
            # Datei zurückschreiben
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(lines))
            
            results["removed"] = unused_imports
            print(f"✅ {file_path}: {len(unused_imports)} ungenutzte Imports entfernt")
        
    except Exception as e:
        results["errors"].append(f"Fehler beim Aufräumen: {e}")
        print(f"❌ {file_path}: Fehler - {e}")
    
    return results

def find_python_files(project_root: str) -> List[Path]:
    """Findet alle Python-Dateien im Projekt"""
    python_files = []
    project_root = Path(project_root)
    
    for root, dirs, files in os.walk(project_root):
        # Verzeichnisse ausschließen
        dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['__pycache__', 'venv', 'node_modules']]
        
        for file in files:
            if file.endswith('.py'):
                python_files.append(Path(root) / file)
    
    return python_files

def main():
    """Hauptfunktion"""
    print("🧹 Import-Cleaner für Backend")
    print("=" * 50)
    
    # Projekt-Root finden
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    
    # Python-Dateien finden
    python_files = find_python_files(project_root)
    print(f"📁 Gefundene Python-Dateien: {len(python_files)}")
    
    # Statistiken
    total_removed = 0
    total_errors = 0
    cleaned_files = 0
    
    # Jede Datei bereinigen
    for file_path in python_files:
        results = clean_file_imports(str(file_path))
        
        if results["removed"]:
            cleaned_files += 1
            total_removed += len(results["removed"])
        
        if results["errors"]:
            total_errors += len(results["errors"])
    
    # Zusammenfassung
    print("\n" + "=" * 50)
    print("📊 ZUSAMMENFASSUNG")
    print(f"✅ Bereinigte Dateien: {cleaned_files}")
    print(f"🗑️ Entfernte Imports: {total_removed}")
    print(f"❌ Fehler: {total_errors}")
    
    if total_removed > 0:
        print(f"\n🎉 Erfolgreich {total_removed} ungenutzte Imports entfernt!")
    else:
        print("\n✨ Alle Imports sind bereits sauber!")

if __name__ == "__main__":
    main() 
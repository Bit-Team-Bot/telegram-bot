"""
Import-Validierungssystem
Erkennt und verhindert Import-Leichen und nicht funktionierende Imports
"""
import ast
import importlib
import logging
import os
from pathlib import Path
from typing import List, Dict, Set, Tuple
import sys

logger = logging.getLogger(__name__)

class ImportValidator:
    """Validierungssystem für Python-Imports"""
    
    def __init__(self, project_root: str = None):
        self.project_root = Path(project_root) if project_root else Path(__file__).parent.parent.parent
        self.valid_imports = set()
        self.invalid_imports = set()
        self.unused_imports = set()
        self.missing_modules = set()
        
    def scan_project_imports(self) -> Dict[str, List[str]]:
        """Scannt alle Imports im Projekt"""
        results = {
            "valid_imports": [],
            "invalid_imports": [],
            "unused_imports": [],
            "missing_modules": []
        }
        
        python_files = self._find_python_files()
        
        for file_path in python_files:
            file_results = self._analyze_file_imports(file_path)
            
            for key in results:
                results[key].extend(file_results.get(key, []))
        
        return results
    
    def _find_python_files(self) -> List[Path]:
        """Findet alle Python-Dateien im Projekt"""
        python_files = []
        
        for root, dirs, files in os.walk(self.project_root):
            # Verzeichnisse ausschließen
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['__pycache__', 'venv', 'node_modules']]
            
            for file in files:
                if file.endswith('.py'):
                    python_files.append(Path(root) / file)
        
        return python_files
    
    def _analyze_file_imports(self, file_path: Path) -> Dict[str, List[str]]:
        """Analysiert Imports in einer einzelnen Datei"""
        results = {
            "valid_imports": [],
            "invalid_imports": [],
            "unused_imports": [],
            "missing_modules": []
        }
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # AST-Parsing
            tree = ast.parse(content)
            
            # Imports extrahieren
            imports = self._extract_imports(tree)
            
            # Import-Namen extrahieren
            import_names = self._extract_import_names(tree)
            
            # Jeden Import validieren
            for import_stmt in imports:
                if self._is_valid_import(import_stmt, file_path):
                    results["valid_imports"].append(f"{file_path}: {import_stmt}")
                else:
                    results["invalid_imports"].append(f"{file_path}: {import_stmt}")
                    results["missing_modules"].append(import_stmt)
            
            # Unused Imports finden
            unused = self._find_unused_imports(import_names, tree)
            results["unused_imports"].extend([f"{file_path}: {imp}" for imp in unused])
            
        except Exception as e:
            logger.error(f"Fehler beim Analysieren von {file_path}: {e}")
            results["invalid_imports"].append(f"{file_path}: PARSE_ERROR - {e}")
        
        return results
    
    def _extract_imports(self, tree: ast.AST) -> List[str]:
        """Extrahiert alle Import-Statements aus dem AST"""
        imports = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                for alias in node.names:
                    if module:
                        imports.append(f"{module}.{alias.name}")
                    else:
                        imports.append(alias.name)
        
        return imports
    
    def _extract_import_names(self, tree: ast.AST) -> Set[str]:
        """Extrahiert die Namen aller importierten Module/Funktionen"""
        import_names = set()
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    import_names.add(alias.asname or alias.name)
            elif isinstance(node, ast.ImportFrom):
                for alias in node.names:
                    import_names.add(alias.asname or alias.name)
        
        return import_names
    
    def _is_valid_import(self, import_stmt: str, file_path: Path) -> bool:
        """Prüft ob ein Import gültig ist"""
        try:
            # Relative Imports behandeln
            if import_stmt.startswith('.'):
                return self._is_valid_relative_import(import_stmt, file_path)
            
            # Absolute Imports
            if import_stmt.startswith('app.'):
                return self._is_valid_app_import(import_stmt, file_path)
            
            # Standard-Library und Third-Party Imports
            return self._is_valid_external_import(import_stmt)
            
        except Exception as e:
            logger.warning(f"Fehler bei Import-Validierung '{import_stmt}': {e}")
            return False
    
    def _is_valid_relative_import(self, import_stmt: str, file_path: Path) -> bool:
        """Prüft relative Imports"""
        try:
            # Relative Import-Pfad berechnen
            dots = len(import_stmt) - len(import_stmt.lstrip('.'))
            module_name = import_stmt[dots:]
            
            # Ziel-Datei finden
            current_dir = file_path.parent
            for _ in range(dots - 1):
                current_dir = current_dir.parent
            
            # Verschiedene mögliche Dateinamen prüfen
            possible_files = [
                current_dir / f"{module_name}.py",
                current_dir / module_name / "__init__.py",
                current_dir / module_name / f"{module_name.split('.')[-1]}.py"
            ]
            
            return any(f.exists() for f in possible_files)
            
        except Exception:
            return False
    
    def _is_valid_app_import(self, import_stmt: str, file_path: Path) -> bool:
        """Prüft app-spezifische Imports"""
        try:
            # app. entfernen
            module_path = import_stmt[4:]  # "app." entfernen
            
            # Verschiedene mögliche Pfade prüfen
            possible_paths = [
                self.project_root / "backend" / "app" / f"{module_path}.py",
                self.project_root / "backend" / "app" / module_path / "__init__.py",
                self.project_root / "backend" / "app" / module_path / f"{module_path.split('.')[-1]}.py"
            ]
            
            return any(p.exists() for p in possible_paths)
            
        except Exception:
            return False
    
    def _is_valid_external_import(self, import_stmt: str) -> bool:
        """Prüft externe Imports"""
        try:
            # Nur den Hauptmodul-Namen prüfen
            main_module = import_stmt.split('.')[0]
            
            # Standard-Library-Module
            stdlib_modules = {
                'os', 'sys', 'json', 'datetime', 'logging', 'pathlib', 
                'typing', 'asyncio', 'sqlalchemy', 'fastapi', 'pydantic',
                'requests', 'telethon', 'pyrogram'
            }
            
            if main_module in stdlib_modules:
                return True
            
            # Versuchen zu importieren
            importlib.import_module(main_module)
            return True
            
        except ImportError:
            return False
        except Exception:
            return False
    
    def _find_unused_imports(self, import_names: Set[str], tree: ast.AST) -> List[str]:
        """Findet ungenutzte Imports"""
        used_names = set()
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Name):
                used_names.add(node.id)
            elif isinstance(node, ast.Attribute):
                # Bei Attributen nur den Basis-Namen prüfen
                if isinstance(node.value, ast.Name):
                    used_names.add(node.value.id)
        
        return list(import_names - used_names)
    
    def validate_specific_file(self, file_path: str) -> Dict[str, List[str]]:
        """Validiert Imports in einer spezifischen Datei"""
        file_path = Path(file_path)
        if not file_path.exists():
            return {"error": [f"Datei nicht gefunden: {file_path}"]}
        
        return self._analyze_file_imports(file_path)
    
    def fix_import_issues(self, file_path: str) -> Dict[str, List[str]]:
        """Versucht Import-Probleme automatisch zu beheben"""
        results = {
            "fixed": [],
            "errors": [],
            "warnings": []
        }
        
        try:
            file_path = Path(file_path)
            if not file_path.exists():
                results["errors"].append(f"Datei nicht gefunden: {file_path}")
                return results
            
            # Datei analysieren
            analysis = self._analyze_file_imports(file_path)
            
            # Ungenutzte Imports entfernen
            if analysis["unused_imports"]:
                self._remove_unused_imports(file_path, analysis["unused_imports"])
                results["fixed"].extend(analysis["unused_imports"])
            
            # Fehlende Module melden
            if analysis["missing_modules"]:
                results["warnings"].extend([
                    f"Fehlendes Modul: {module}" 
                    for module in analysis["missing_modules"]
                ])
            
        except Exception as e:
            results["errors"].append(f"Fehler beim Beheben der Import-Probleme: {e}")
        
        return results
    
    def _remove_unused_imports(self, file_path: Path, unused_imports: List[str]):
        """Entfernt ungenutzte Imports aus einer Datei"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # Zeilen mit ungenutzten Imports markieren
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
                f.writelines(lines)
            
            logger.info(f"Ungenutzte Imports aus {file_path} entfernt")
            
        except Exception as e:
            logger.error(f"Fehler beim Entfernen ungenutzter Imports: {e}")
    
    def generate_import_report(self) -> str:
        """Generiert einen detaillierten Import-Report"""
        results = self.scan_project_imports()
        
        report = []
        report.append("=== IMPORT-VALIDIERUNGS-REPORT ===")
        report.append(f"Projekt: {self.project_root}")
        report.append(f"Datum: {datetime.now().isoformat()}")
        report.append("")
        
        # Zusammenfassung
        report.append("ZUSAMMENFASSUNG:")
        report.append(f"- Gültige Imports: {len(results['valid_imports'])}")
        report.append(f"- Ungültige Imports: {len(results['invalid_imports'])}")
        report.append(f"- Ungenutzte Imports: {len(results['unused_imports'])}")
        report.append(f"- Fehlende Module: {len(results['missing_modules'])}")
        report.append("")
        
        # Details
        if results['invalid_imports']:
            report.append("UNGÜLTIGE IMPORTS:")
            for imp in results['invalid_imports']:
                report.append(f"  - {imp}")
            report.append("")
        
        if results['unused_imports']:
            report.append("UNGENUTZTE IMPORTS:")
            for imp in results['unused_imports']:
                report.append(f"  - {imp}")
            report.append("")
        
        if results['missing_modules']:
            report.append("FEHLENDE MODULE:")
            for module in set(results['missing_modules']):
                report.append(f"  - {module}")
            report.append("")
        
        return "\n".join(report)

# Globale Instanz
import_validator = ImportValidator()

def validate_project_imports():
    """Validiert alle Imports im Projekt"""
    return import_validator.scan_project_imports()

def generate_import_report():
    """Generiert einen Import-Report"""
    return import_validator.generate_import_report() 
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


LANGUAGE_CONFIG = {
    "python": {"label": "Python 3", "command": "python", "source": "solution.py"},
    "javascript": {"label": "JavaScript (Node.js)", "command": "node", "source": "solution.js"},
    "typescript": {"label": "TypeScript", "command": "node", "source": "solution.ts"},
    "java": {"label": "Java 17", "command": "javac", "source": "Main.java"},
}

DEFAULT_STARTERS = {
    "python": "# Read from standard input and print the answer\n",
    "javascript": "// Read with fs.readFileSync(0, 'utf8') and print the answer\n",
    "typescript": "import * as fs from 'fs';\nconst input: string = fs.readFileSync(0, 'utf8').trim();\n// Write your solution here\n",
    "java": "import java.io.*;\nimport java.util.*;\n\npublic class Main {\n    public static void main(String[] args) throws Exception {\n        Scanner sc = new Scanner(System.in);\n        // Write your solution here\n    }\n}\n",
}


def _java_tool(name):
    configured = os.environ.get("JAVA_HOME")
    if configured and (Path(configured) / "bin" / f"{name}.exe").exists():
        return str(Path(configured) / "bin" / f"{name}.exe")
    java_root = Path(os.environ.get("ProgramFiles", "C:/Program Files")) / "Java"
    matches = sorted(java_root.glob(f"jdk*/bin/{name}.exe"), reverse=True)
    return str(matches[0]) if matches else shutil.which(name)


def _typescript_compiler():
    return Path(__file__).resolve().parents[2] / "frontend" / "node_modules" / "typescript" / "bin" / "tsc"


def _typescript_types():
    return Path(__file__).resolve().parents[2] / "frontend" / "node_modules" / "@types"


def _safe_environment():
    keys = ("PATH", "SYSTEMROOT", "WINDIR", "TEMP", "TMP", "COMSPEC", "PATHEXT")
    return {key: os.environ[key] for key in keys if key in os.environ}


def available_languages():
    available = []
    for value, config in LANGUAGE_CONFIG.items():
        if value == "java":
            ready = bool(_java_tool("java") and _java_tool("javac"))
        elif value == "typescript":
            ready = bool(shutil.which("node") and _typescript_compiler().exists())
        else:
            command = sys.executable if value == "python" else config["command"]
            ready = value == "python" or bool(shutil.which(command))
        if ready:
            available.append({"value": value, "label": config["label"]})
    return available


def _prepare(language, source, folder):
    """Compile when required and return (run command, compilation error)."""
    if language == "python":
        return [sys.executable, str(source)], ""
    if language == "javascript":
        return [shutil.which("node"), str(source)], ""
    if language == "typescript":
        compile_process = subprocess.run(
            [shutil.which("node"), str(_typescript_compiler()), str(source), "--target", "ES2020", "--module", "commonjs", "--skipLibCheck", "--typeRoots", str(_typescript_types()), "--types", "node", "--outDir", folder],
            capture_output=True, text=True, timeout=20, cwd=folder,
            env=_safe_environment(),
        )
        if compile_process.returncode:
            return None, (compile_process.stderr or compile_process.stdout)[:2000]
        return [shutil.which("node"), str(Path(folder) / "solution.js")], ""
    if language == "java":
        compile_process = subprocess.run(
            [_java_tool("javac"), str(source)], capture_output=True, text=True,
            timeout=20, cwd=folder, env=_safe_environment(),
        )
        if compile_process.returncode:
            return None, (compile_process.stderr or compile_process.stdout)[:2000]
        return [_java_tool("java"), "-cp", folder, "Main"], ""
    return None, "Unsupported language"


def run_code(code, language, test_cases):
    """Compile and run stdin/stdout solutions. Isolate this worker in production."""
    config = LANGUAGE_CONFIG.get(language)
    if not config or language not in {item["value"] for item in available_languages()}:
        return [{"passed": False, "actual": "", "expected": "", "error": "This language is unavailable on the evaluation server"}]
    results = []
    with tempfile.TemporaryDirectory(prefix="campushire-") as folder:
        source = Path(folder) / config["source"]
        source.write_text(code, encoding="utf-8")
        try:
            command, compile_error = _prepare(language, source, folder)
        except subprocess.TimeoutExpired:
            command, compile_error = None, "Compilation time limit exceeded"
        except Exception as exc:
            command, compile_error = None, str(exc)[:2000]
        if compile_error:
            return [{"passed": False, "actual": "", "expected": str(case.get("output", "")), "error": f"Compilation error: {compile_error}"} for case in test_cases]
        for case in test_cases:
            try:
                proc = subprocess.run(command, input=str(case.get("input", "")), text=True, capture_output=True, timeout=3, cwd=folder, env=_safe_environment())
                actual, expected = proc.stdout.strip(), str(case.get("output", "")).strip()
                results.append({"passed": proc.returncode == 0 and actual == expected, "actual": actual[:500], "expected": expected, "error": proc.stderr[:500]})
            except subprocess.TimeoutExpired:
                results.append({"passed": False, "actual": "", "expected": str(case.get("output", "")), "error": "Time limit exceeded"})
            except Exception as exc:
                results.append({"passed": False, "actual": "", "expected": str(case.get("output", "")), "error": str(exc)[:500]})
    return results

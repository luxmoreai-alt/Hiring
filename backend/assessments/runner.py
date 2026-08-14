import base64
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, urlparse
from urllib.request import Request, urlopen


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

JUDGE0_LANGUAGE_PREFIX = "judge0:"
_judge0_languages_cache = {"expires": 0, "languages": []}


def _judge0_url(path):
    return f"{os.environ['JUDGE0_API_URL'].rstrip('/')}/{path.lstrip('/')}"


def _judge0_request(path, method="GET", payload=None, timeout=15):
    """Call a self-hosted Judge0 API or the authenticated RapidAPI gateway."""
    # RapidAPI/Judge0's edge protection rejects Python urllib's default user agent.
    headers = {
        "Accept": "application/json",
        "User-Agent": "LuxmoreTalentForge/1.0 (+https://luxmore.ai)",
    }
    token = os.environ.get("JUDGE0_AUTH_TOKEN")
    if token:
        headers["X-Auth-Token"] = token
    rapidapi_key = os.environ.get("JUDGE0_RAPIDAPI_KEY")
    if rapidapi_key:
        headers["X-RapidAPI-Key"] = rapidapi_key
        headers["X-RapidAPI-Host"] = os.environ.get("JUDGE0_RAPIDAPI_HOST") or urlparse(os.environ["JUDGE0_API_URL"]).netloc
    data = None
    if payload is not None:
        headers["Content-Type"] = "application/json"
        data = json.dumps(payload).encode("utf-8")
    request = Request(_judge0_url(path), data=data, headers=headers, method=method)
    try:
        with urlopen(request, timeout=timeout) as response:
            return json.loads(response.read().decode("utf-8"))
    except (HTTPError, URLError, TimeoutError, json.JSONDecodeError) as exc:
        raise RuntimeError("The code evaluator is unavailable") from exc


def _judge0_languages():
    """Return the evaluator's language catalogue, cached to keep question loads fast."""
    if not os.environ.get("JUDGE0_API_URL"):
        return []
    now = time.monotonic()
    if now < _judge0_languages_cache["expires"]:
        return _judge0_languages_cache["languages"]
    try:
        languages = _judge0_request("languages")
        result = [
            {"value": f"{JUDGE0_LANGUAGE_PREFIX}{item['id']}", "label": item["name"]}
            for item in languages
            if isinstance(item, dict) and item.get("id") is not None and item.get("name")
        ]
        _judge0_languages_cache.update(expires=now + 300, languages=result)
        return result
    except RuntimeError:
        # Keep the last known catalogue available during a brief evaluator outage.
        return _judge0_languages_cache["languages"]


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
    judge0_languages = _judge0_languages()
    if judge0_languages:
        return judge0_languages
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


def _decode_judge0(value):
    if not value:
        return ""
    try:
        return base64.b64decode(value).decode("utf-8", errors="replace")
    except (ValueError, UnicodeDecodeError):
        return str(value)


def _run_judge0(code, language, test_cases):
    language_id = language.removeprefix(JUDGE0_LANGUAGE_PREFIX)
    if not language_id.isdigit():
        return [{"passed": False, "actual": "", "expected": str(case.get("output", "")), "error": "Unsupported language"} for case in test_cases]
    results = []
    for case in test_cases:
        try:
            submission = _judge0_request(
                f"submissions?{urlencode({'base64_encoded': 'true', 'wait': 'true'})}",
                method="POST",
                payload={
                    "language_id": int(language_id),
                    "source_code": base64.b64encode(code.encode("utf-8")).decode("ascii"),
                    "stdin": base64.b64encode(str(case.get("input", "")).encode("utf-8")).decode("ascii"),
                },
                timeout=25,
            )
            actual = _decode_judge0(submission.get("stdout")).strip()
            expected = str(case.get("output", "")).strip()
            status = submission.get("status", {})
            accepted = status.get("id") == 3
            error = _decode_judge0(submission.get("compile_output") or submission.get("stderr") or status.get("description"))
            results.append({"passed": accepted and actual == expected, "actual": actual[:500], "expected": expected, "error": "" if accepted else error[:500]})
        except RuntimeError as exc:
            results.append({"passed": False, "actual": "", "expected": str(case.get("output", "")), "error": str(exc)})
    return results


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
    if language.startswith(JUDGE0_LANGUAGE_PREFIX):
        if language not in {item["value"] for item in available_languages()}:
            return [{"passed": False, "actual": "", "expected": "", "error": "This language is unavailable on the evaluation server"}]
        return _run_judge0(code, language, test_cases)
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

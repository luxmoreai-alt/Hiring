"""Install Python and frontend dependencies in local or Vercel environments."""
import shutil
import subprocess
import sys


def run(command):
    print("+", " ".join(command), flush=True)
    subprocess.run(command, check=True)


uv = shutil.which("uv")
if uv:
    run([uv, "pip", "install", "--system", "-r", "requirements.txt"])
else:
    run([sys.executable, "-m", "pip", "install", "--disable-pip-version-check", "-r", "requirements.txt"])

npm = shutil.which("npm") or shutil.which("npm.cmd")
if not npm:
    raise RuntimeError("npm is required to build the frontend")
run([npm, "--prefix", "frontend", "install", "--no-audit", "--no-fund"])

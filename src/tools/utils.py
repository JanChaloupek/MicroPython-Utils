import sys
import subprocess
import shutil

# ANSI barvy (funguje na Win 10+, Linux, macOS)
RESET = "\033[0m"
FG_INFO = "\033[36m"
FG_OK = "\033[32m"
FG_ERR = "\033[31m"
FG_FILE = "\033[33m"
FG_DIR = "\033[36m"
FG_SIZE = "\033[90m"

def color(text, c):
    return f"{c}{text}{RESET}"

def info(msg):
    print(color(msg, FG_INFO))

def ok(msg):
    print(color(msg, FG_OK))

def error(msg):
    print(color(msg, FG_ERR), file=sys.stderr)

def banner(name, version=None):
    line = "-" * 38
    print(line)
    if version:
        print(f"{name} - verze: {version}")
    else:
        print(name)
    print(line)

def run_cmd(cmd, capture_output=False):
    try:
        if capture_output:
            result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            return result.returncode, result.stdout, result.stderr
        else:
            result = subprocess.run(cmd)
            return result.returncode, None, None
    except FileNotFoundError:
        error(f"Prikaz nenalezen: {cmd[0]}")
        return 1, None, None

def ensure_mpremote():
    if shutil.which("mpremote") is None:
        error("mpremote neni v PATH. Nainstaluj: pip install mpremote")
        sys.exit(1)

def detect_port():
    """
    Minimalni multiplatformni detekce portu.
    Pro zacatek: spolehni se na mpremote 'connect auto'.
    Pozdeji muzeme pridat chytrejsi logiku (pyserial, atd.).
    """
    return "auto"

def mpremote(args, capture_output=False):
    ensure_mpremote()
    cmd = ["mpremote"] + args
    return run_cmd(cmd, capture_output=capture_output)

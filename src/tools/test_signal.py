import signal
import subprocess
import sys

def _signal_handler(signum, frame):
    print(f"[CLI] Zachycen signal: {signum}")
    sys.stdout.flush()

def run(args):
    # Registrace handlerů
    signal.signal(signal.SIGINT, _signal_handler)
    signal.signal(signal.SIGBREAK, _signal_handler)

    print("[CLI] Spoustim mpremote...")
    sys.stdout.flush()

    # Spustíme mpremote repl
    proc = subprocess.Popen(
        ["mpremote", "repl"],
        stdin=sys.stdin,
        stdout=sys.stdout,
        stderr=sys.stderr
    )

    try:
        proc.wait()
    except KeyboardInterrupt:
        print("[CLI] KeyboardInterrupt v hlavnim programu")
        sys.stdout.flush()

    print("[CLI] mpremote skoncil, konec testu.")

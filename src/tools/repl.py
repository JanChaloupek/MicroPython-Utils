from . import utils
import subprocess
import sys

def run(argv):
    utils.banner("repl", version="1.0")

    port = utils.detect_port()
    utils.info(f"Pouzivam port: {port}")
    utils.info("Spoustim REPL... (ukonceni: Ctrl+X nebo Ctrl+])")

    # Přímé předání stdin/stdout do mpremote
    try:
        p = subprocess.Popen(
            ["mpremote", "connect", port, "repl"],
            stdin=sys.stdin,
            stdout=sys.stdout,
            stderr=sys.stderr
        )
        p.wait()
        return p.returncode

    except KeyboardInterrupt:
        utils.info("REPL ukoncen uzivatelem.")
        return 0

    except Exception as e:
        utils.error(f"Chyba pri spousteni REPL: {e}")
        return 1

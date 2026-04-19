from . import utils

def run(argv):
    utils.banner("run_main", version="1.2")

    port = utils.detect_port()
    utils.info(f"Pouzivam port: {port}")
    utils.info("Spoustim main.py...")

    # Reload + spusteni main.py
    code, out, err = utils.mpremote(
        ["connect", port, "exec", "import sys; sys.modules.pop('main', None); import main"],
        capture_output=True
    )

    if out:
        print(out.strip())

    if code != 0 or (err and "Traceback" in err):
        utils.error("Spusteni main.py selhalo.")
        if err:
            print(err.strip())
        return 1

    utils.ok("main.py dokoncen.")
    return 0

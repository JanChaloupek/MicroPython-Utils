from . import utils

MP_FS_INFO = r"""
import os
s = os.statvfs("/")
total = s[0] * s[2]
free  = s[0] * s[3]
print("Total:", total, "B")
print("Free :", free,  "B")
"""

def run(argv):
    utils.banner("check", version="1.0")

    port = utils.detect_port()
    utils.info(f"Pouzivam port: {port}")

    # 1) Test REPL
    utils.info("Testuji REPL...")
    code, _, _ = utils.mpremote(["connect", port, "exec", "pass"])
    if code != 0:
        utils.error("Zarizeni nereaguje na REPL.")
        return 1
    utils.ok("REPL OK")

    # 2) Info o filesystemu
    utils.info("Informace o filesystemu:")
    code, out, err = utils.mpremote(["connect", port, "exec", MP_FS_INFO], capture_output=True)
    if code != 0:
        utils.error("Nepodarilo se ziskat informace o filesystemu.")
        if err:
            utils.error(err.strip())
        return 1
    print(out.strip())

    # 3) Stromovy vypis (reuse list.py)
    utils.info("Obsah zarizeni:")
    from . import list as list_mod
    list_mod.run([])

    utils.ok("Diagnostika dokoncena.")
    return 0

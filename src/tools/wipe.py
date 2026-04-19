from . import utils

MP_WIPE = r"""
import os

def wipe_dir(p):
    try:
        items = os.listdir(p)
    except:
        return
    for n in items:
        full = p + '/' + n if p != '/' else '/' + n
        try:
            st = os.stat(full)
        except:
            continue
        mode = st[0]
        if mode & 0x4000:
            wipe_dir(full)
            try:
                os.rmdir(full)
            except:
                pass
        else:
            try:
                os.remove(full)
            except:
                pass

wipe_dir("/")
"""

def run(argv):
    utils.banner("wipe", version="1.0")

    port = utils.detect_port()
    utils.info(f"Pouzivam port: {port}")
    utils.info("Mazani vsech souboru na zarizeni...")

    code, _, err = utils.mpremote(["connect", port, "exec", MP_WIPE], capture_output=True)
    if code != 0:
        utils.error("Mazani selhalo.")
        if err:
            utils.error(err.strip())
        return 1

    utils.ok("Mazani dokonceno.")
    return 0

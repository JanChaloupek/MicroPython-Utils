from . import utils
from . import wipe as wipe_mod
from . import upload as upload_mod
from . import list as list_mod

def run(argv):
    utils.banner("setup_project", version="1.0")

    utils.info("KROK 1/3: wipe")
    if wipe_mod.run([]) != 0:
        utils.error("wipe selhal.")
        return 1

    utils.info("KROK 2/3: upload")
    if upload_mod.run([]) != 0:
        utils.error("upload selhal.")
        return 1

    utils.info("KROK 3/3: list")
    if list_mod.run([]) != 0:
        utils.error("list selhal.")
        return 1

    utils.ok("Setup complete. Device is ready.")
    return 0

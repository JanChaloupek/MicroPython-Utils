import os
from . import utils

def run(argv):
    utils.banner("upload_main", version="1.0")

    main_file = "main.py"
    if not os.path.exists(main_file):
        utils.error("Soubor main.py nebyl nalezen v aktualni slozce.")
        return 1

    port = utils.detect_port()
    utils.info(f"Pouzivam port: {port}")
    print(f"Nahravam soubor: {utils.color(main_file, utils.FG_FILE)}")

    code, _, _ = utils.mpremote(["connect", port, "cp", main_file, ":"])
    if code != 0:
        utils.error("Nahrani main.py selhalo.")
        return 1

    utils.ok("main.py uspesne nahran.")
    return 0

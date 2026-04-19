import os
from . import utils

CONFIG_NAME = "upload_config.txt"

def find_config():
    """
    Hleda upload_config.txt na vice mistech:
    1) aktualni adresar
    2) root projektu (tam, kde je soubor mpy)
    3) tools/
    """
    search_paths = []

    # 1) aktualni adresar
    search_paths.append(os.getcwd())

    # 2) root projektu = adresar, kde lezi soubor mpy
    mpy_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    search_paths.append(mpy_path)

    # 3) tools/
    tools_path = os.path.abspath(os.path.dirname(__file__))
    search_paths.append(tools_path)

    for path in search_paths:
        candidate = os.path.join(path, CONFIG_NAME)
        if os.path.exists(candidate):
            return candidate

    return None


def run(argv):
    utils.banner("upload", version="1.1")

    port = utils.detect_port()
    utils.info(f"Pouzivam port: {port}")

    config_path = find_config()
    if not config_path:
        utils.error("Soubor upload_config.txt nebyl nalezen.")
        utils.info("Hledal jsem v:")
        print("  - aktualni adresar")
        print("  - root projektu (kde je mpy)")
        print("  - tools/")
        return 1

    utils.info(f"Pouzivam konfiguraci: {config_path}")

    with open(config_path, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f.readlines()]

    items = [l for l in lines if l and not l.startswith("#")]

    if not items:
        utils.error("V konfiguraci nejsou zadne polozky k nahrani.")
        return 1

    utils.info("Zahajuji nahravani...")

    for item in items:
        if not os.path.exists(item):
            utils.error(f"Preskakuji (nenalezeno): {item}")
            continue

        if os.path.isdir(item):
            print(f"Nahravam adresar: {utils.color(item, utils.FG_DIR)}")
            code, _, _ = utils.mpremote(["connect", port, "cp", "-r", item, ":"])
        else:
            print(f"Nahravam soubor: {utils.color(item, utils.FG_FILE)}")
            code, _, _ = utils.mpremote(["connect", port, "cp", item, ":"])

        if code != 0:
            utils.error(f"Nahravani polozky selhalo: {item}")
            return 1

    utils.ok("Nahravani dokonceno.")
    return 0

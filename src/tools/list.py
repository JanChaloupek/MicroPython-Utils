import json
from . import utils

MP_CODE = r"""
import os, json

def walk(p):
    result = []
    try:
        items = os.listdir(p)
    except:
        return result

    dirs = []
    files = []

    for n in items:
        full = p + '/' + n if p != '/' else '/' + n
        try:
            st = os.stat(full)
        except:
            continue

        mode = st[0]
        if mode & 0x4000:
            dirs.append(n)
        else:
            files.append((n, st[6]))

    result.append((p, dirs, files))

    for d in dirs:
        sub = p + '/' + d if p != '/' else '/' + d
        result.extend(walk(sub))

    return result

print(json.dumps(walk('/')))
"""

def run(argv):
    utils.banner("list", version="1.6")

    port = utils.detect_port()
    utils.info(f"Pouzivam port: {port}")
    utils.info("Ziskavam seznam souboru...")

    code, out, err = utils.mpremote(["connect", port, "exec", MP_CODE], capture_output=True)
    if code != 0 or not out:
        utils.error("Nepodarilo se ziskat seznam souboru.")
        if err:
            utils.error(err.strip())
        return 1

    text = out.strip()
    start = text.find("[")
    end = text.rfind("]")
    if start < 0 or end <= start:
        utils.error("JSON blok nenalezen.")
        return 1

    data = json.loads(text[start:end+1])

    # Postavime strom
    index = {}
    for path, dirs, files in data:
        index[path] = {
            "path": path,
            "name": path.split("/")[-1] if path != "/" else "/",
            "dirs": dirs,
            "files": files,
            "children": []
        }

    for path, node in index.items():
        for d in node["dirs"]:
            child_path = f"{path}/{d}" if path != "/" else f"/{d}"
            if child_path in index:
                node["children"].append(index[child_path])

    root = index.get("/", None)
    if not root:
        utils.error("Korenovy adresar '/' nenalezen.")
        return 1

    # ----------------------------------------------------
    # 1) Zjistime maximalni sirku leve casti (bez barev!)
    # ----------------------------------------------------
    def collect_meta(node, prefix, left_widths, sizes):
        # soubory
        for i, (name, size) in enumerate(node["files"]):
            is_last = (i == len(node["files"]) - 1 and not node["children"])
            branch = "└── " if is_last else "├── "
            left_plain = prefix + branch + name
            left_widths.append(len(left_plain))
            sizes.append(size)

        # adresare
        for i, child in enumerate(node["children"]):
            is_last = (i == len(node["children"]) - 1)
            branch = "└── " if is_last else "├── "
            left_plain = prefix + branch + child["name"] + "/"
            left_widths.append(len(left_plain))

            new_prefix = prefix + ("    " if is_last else "│   ")
            collect_meta(child, new_prefix, left_widths, sizes)

    left_widths = []
    sizes = []
    collect_meta(root, "", left_widths, sizes)

    max_left = max(left_widths) if left_widths else 0
    max_size = len(str(max(sizes))) if sizes else 0

    # ----------------------------------------------------
    # 2) Tisk stromu (barvy jen na jménech)
    # ----------------------------------------------------
    def print_tree(node, prefix=""):
        files = node["files"]
        children = node["children"]

        # soubory
        for i, (name, size) in enumerate(files):
            is_last = (i == len(files) - 1 and not children)
            branch = "└── " if is_last else "├── "

            left_plain = prefix + branch + name
            left_padded_plain = left_plain.ljust(max_left)

            # nahradíme jen jméno barevnou verzí
            name_start = left_padded_plain.rfind(name)
            left_colored = (
                left_padded_plain[:name_start]
                + utils.color(name, utils.FG_FILE)
                + left_padded_plain[name_start + len(name):]
            )

            size_str = str(size).rjust(max_size)
            print(f"{left_colored}  {utils.color('(' + size_str + ' B)', utils.FG_SIZE)}")

        # adresare
        for i, child in enumerate(children):
            is_last = (i == len(children) - 1)
            branch = "└── " if is_last else "├── "

            left_plain = prefix + branch + child["name"] + "/"
            print(
                prefix + branch +
                utils.color(child["name"] + "/", utils.FG_DIR)
            )

            new_prefix = prefix + ("    " if is_last else "│   ")
            print_tree(child, new_prefix)

    print_tree(root)

    utils.ok("Hotovo.")
    return 0

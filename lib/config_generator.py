import re
import os
from pathlib import Path

ADDONS_DIR = os.path.abspath('../..')

ACF_GUNS_PATHS = ADDONS_DIR + "/acf/lua/acf/shared/guns"
STUBS_PATH = ADDONS_DIR + "/cfc_acf_stubber/lua/cfc_acf_stubber/stubs"

PATTERN_DEFINE_GUN_CLASS = "ACF_defineGunClass\\(\"([\\w\\.]+)\", {\\s*\n([^\\)]+)} \\)"
PATTERN_DEFINE_GUN = "ACF_defineGun\\(\"([\\w\\.]+)\", {\\s*\n([^\\)]+)} \\)"

PATTERN_KEY_VALUES = "(?:\\s+([\\w]+)\\s?=\\s?(.+))|(})"

PATTERN_COMMENT_BLOCK = "--\\[\\[[^\\]]+\\]\\](?:--)?"
PATTERN_COMMENT_SINGLE = "--[^\n]+"

LUA_HEADER = """AddCSLuaFile()

DATA = {
    enabled = true,
"""
LUA_FOOTER = "}"

def remove_comments(commented):
    no_block_comments = re.sub(PATTERN_COMMENT_BLOCK, '', commented)
    uncommented = re.sub(PATTERN_COMMENT_SINGLE, '', no_block_comments)
    return uncommented

def parse_table(key_values):
    out = {}
    tabs = [out]
    for res in re.findall(PATTERN_KEY_VALUES, key_values):
        cur_tab = tabs[-1]
        if res[2] == "}":
            del tabs[-1]
            continue
        key = res[0]
        value = res[1].strip()
        if value == "{":
            cur_tab[key] = {}
            tabs.append(cur_tab[key])
        else:
            if value[-1] == ",":
                value = value[:-1]
            cur_tab[key] = value
    return out

def get_class_name_and_data(raw):
    res = re.search(PATTERN_DEFINE_GUN_CLASS, raw)
    gun_class = res.group(1)
    key_values = res.group(2)
    data = parse_table(key_values)
    return gun_class, data

def get_gun_name_and_data(raw):
    out = []
    for res in re.findall(PATTERN_DEFINE_GUN, raw):
        gun_name = res[0]
        key_values = res[1]
        gun_data = parse_table(key_values)
        out.append([gun_name, gun_data])
    return out

def data_to_lua(data, indent=""):
    out = ""
    for key in data:
        value = data[key]
        out += indent + key + " = "
        if type(value) is dict:
            out += "{\n" + data_to_lua(value, indent + "    ") + indent + "},\n"
        else:
            out += value + ",\n"
    return out

def name_to_folder(name):
    name = name[1:-1]
    name = name.replace( " ", "_" )
    name = name.lower()
    return name

def main():
    for filename in os.listdir(ACF_GUNS_PATHS):
        with open(ACF_GUNS_PATHS + "/" + filename) as f:
            data = f.read()
        data = remove_comments(data)
        gun_class, class_data = get_class_name_and_data( data )
        gun_folder = name_to_folder(class_data["name"] or gun_class)

        Path(STUBS_PATH + "/" + gun_folder).mkdir(parents=True, exist_ok=True)

        for obj in get_gun_name_and_data(data):
            gun_name = obj[0]
            gun_dataAlone = obj[1]
            gun_data = {**class_data, **gun_dataAlone}

            lua = LUA_HEADER + data_to_lua(gun_data, "    ") + LUA_FOOTER
            lua_path = Path(STUBS_PATH + "/" + gun_folder + "/" + gun_name + ".lua")
            if lua_path.exists():
                continue
            with open(lua_path, "w") as f:
                f.write(lua)

if __name__ == "__main__":
    main()

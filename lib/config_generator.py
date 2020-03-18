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

def removeComments( commented ):
	noBlockComments = ''.join( re.split( PATTERN_COMMENT_BLOCK, commented ) )
	uncommented = ''.join( re.split( PATTERN_COMMENT_SINGLE, noBlockComments ) )
	return uncommented

def parseTable( keyValues ):
	out = {}
	tabs = [out]
	for res in re.findall( PATTERN_KEY_VALUES, keyValues ):
		curTab = tabs[-1]
		if res[2] == "}":
			del tabs[-1]
			continue
		key = res[0]
		value = res[1].strip()
		if value == "{":
			curTab[key] = {}
			tabs.append( curTab[key] )
		else:
			if value[-1] == ",":
				value = value[:-1]
			curTab[key] = value
	return out

def getClassNameAndData( raw ):
	res = re.search( PATTERN_DEFINE_GUN_CLASS, raw )
	gunClass = res.group(1)
	keyValues = res.group(2)
	data = parseTable( keyValues )
	return gunClass, data

def getGunNameAndData( raw ):
	out = []
	for res in re.findall( PATTERN_DEFINE_GUN, raw ):
		gunName = res[0]
		keyValues = res[1]
		gunData = parseTable( keyValues )
		out.append( [gunName, gunData] )
	return out

def dataToLua( data, indent = "" ):
	out = ""
	for key in data:
		value = data[key]
		out += indent + key + " = "
		if type(value) is dict:
			out += "{\n" + dataToLua( value, indent + "    " ) + indent + "},\n"
		else:
			out += value + ",\n"
	return out

def nameToFolder( name ):
	name = name[1:-1]
	name = name.replace( " ", "_" )
	name = name.lower()
	return name

def main():
	for filename in os.listdir( ACF_GUNS_PATHS ):
		with open( ACF_GUNS_PATHS + "/" + filename ) as f:
			data = f.read()
		data = removeComments( data )
		gunClass, classData = getClassNameAndData( data )
		gunFolder = nameToFolder( classData["name"] or gunClass )

		Path( STUBS_PATH + "/" + gunFolder ).mkdir( parents = True, exist_ok = True )

		for obj in getGunNameAndData( data ):
			gunName = obj[0]
			gunDataAlone = obj[1]
			gunData = {**classData, **gunDataAlone}

			lua = LUA_HEADER + dataToLua( gunData, "    " ) + LUA_FOOTER
			luaPath = Path( STUBS_PATH + "/" + gunFolder + "/" + gunName + ".lua" )
			if luaPath.exists():
				continue
			with open( luaPath, "w" ) as f:
				f.write( lua )

if __name__ == "__main__":
	main()
	
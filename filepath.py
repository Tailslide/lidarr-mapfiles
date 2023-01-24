import os
import re
import shutil
from pathlib import PureWindowsPath   
import merge

ROOTFOLDERPATH = os.getenv('ROOTFOLDERPATH')
LOCALFOLDERPATH= os.getenv('LOCALFOLDERPATH')

def renameFolder(src,dest):
    if os.path.exists(dest): # directory exists, merge them
        #try:
            merge.merge(src,dest)
            #shutil.copytree(src, dest, dirs_exist_ok=False)
            return True
        # except FileExistsError as err:
        #     print(f"File exists, can't merge folders. Manually fix this folder. {err=}, {type(err)=}")
        #     return False
    else:
        shutil.move(src,dest)
        return True

def WinSafePath(path):
    return PureWindowsPath(path.replace(":","_"))

def getLocalFileFromPath(path):
    localpath=path.replace(ROOTFOLDERPATH,LOCALFOLDERPATH)
    return localpath


def getLocalAlbumPathFromPath(path):
   localfolder= LOCALFOLDERPATH #[:-1] if LOCALFOLDERPATH.endswith('\\') else LOCALFOLDERPATH
   albumpath=path.replace(ROOTFOLDERPATH,"")
   splits = albumpath.split("/")
   album=splits[1]
   parsed = re.findall(r"^.*\(\d{4}\)",album)
   if (len(parsed) > 0):
    return os.path.join(localfolder, splits[0], parsed[0])
   else:
    return os.path.join(localfolder, splits[0], album)

def _ireplace(old, new, text):
    idx = 0
    while idx < len(text):
        index_l = text.lower().find(old.lower(), idx)
        if index_l == -1:
            return text
        text = text[:index_l] + new + text[index_l + len(old):]
        idx = index_l + len(new) 
    return text

def getAlbumNoParenFromPath(path):
    temp = getAlbumFromPath(path)
    parsed= re.sub("[\(\[].*?[\)\]]","",temp).strip()
    parsed= _ireplace("disk 1","", parsed)
    parsed= _ireplace("disk 2","", parsed)
    parsed= _ireplace("disk 3","", parsed)
    parsed= _ireplace("disk 4","", parsed)
    parsed= _ireplace("disk 5","", parsed)
    return parsed

def _getAlbumAndYearFromPath(path):
    albumpath=path.replace(ROOTFOLDERPATH,"")
    splits = albumpath.split("/")
    album=splits[1]
    parsed= re.findall(r"^(.*)\((\d{4})\)$", album)
    year = None
    if (len(parsed) > 0):
        album = str(parsed[0][0]).strip()
        if (len(parsed[0]) > 1):
            year = int(parsed[0][1])
        else:
            year = None
    if (year is None):
        year=""
    album = album.lower().strip()

    return album, year

## TODO: Optimize

def getAlbumFromPath(path):
    return _getAlbumAndYearFromPath(path)[0]

def getYearFromPath(path):
    return _getAlbumAndYearFromPath(path)[1]


def getArtistFromPath(path):
    albumpath=path.replace(ROOTFOLDERPATH,"")
    splits = albumpath.split("/")
    return splits[0]

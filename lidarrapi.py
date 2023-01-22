import requests
import urllib.parse
import json
import os

LIDARRAPIKEY = os.getenv('LIDARRAPIKEY')
LIDARRURL = os.getenv('LIDARRURL')
ROOTFOLDERPATH = os.getenv('ROOTFOLDERPATH')

requestheaders =    {
            "X-Api-Key":LIDARRAPIKEY,
            "X-Requested-With":"XMLHttpRequest",
            "Accept"  : "*/*",
            "Accept-Language" : "en-US,en;q=0.9",
            "Pragma": "no-cache",
            "Connection": "keep-alive",
            "Cache-Control": "no-cache",
        }
prefix = LIDARRURL

def getUnmappedFiles():    
    response = requests.get(prefix + "trackFile?unmapped=true",  headers=requestheaders)
    if (response.status_code != 200):
        print("Error", response.status_code)
        raise Exception("API Error", response) 
    else:
        return response.json()

def getArtists():
    requrl = prefix + "artist"
    response = requests.get(requrl,  headers=requestheaders)
    if (response.status_code != 200):
        print("Error", response.status_code)
        raise Exception("API Error", response) 
    else:
        return response.json()

def addAlbum(newalbum):
    requrl = prefix + "album"
    newalbum["addOptions"] = { "searchForNewAlbum": False }

    response = requests.post(requrl,  headers=requestheaders, json=newalbum)
    if (not response.ok):
        print("Error adding album ", response.reason, response.text)
        return None
    else:
        return response.json()


def addArtist(newartist):
    requrl = prefix + "artist"
    newartist["addOptions"] = { "searchForMissingAlbums": False, "monitor": "none" }
    newartist["qualityProfileId"] = 1
    newartist["metadataProfileId"] = 1
    newartist["rootFolderPath"] =  ROOTFOLDERPATH

    response = requests.post(requrl,  headers=requestheaders, json=newartist)
    if (not response.ok):
        print("Error adding artist ", response.reason, response.text)
        return None
    else:
        return response.json()


def getArtistAlbums(artistId):
    response = requests.get(prefix + "album?artistId=" + str(artistId),   headers=requestheaders)
    if (response.status_code != 200):
        print("Error", response.status_code)
        raise Exception("API Error", response) 
    else:
        return response.json()

def getSearchResultByGuid(guid):
    params = {'term': "lidarr:" + guid}
    enc = urllib.parse.urlencode(params)
    requrl = prefix + "search?" + enc
    response = requests.get(requrl,  headers=requestheaders)
    if (response.status_code != 200):
        print("Error", response.status_code)
        raise Exception("API Error", response) 
    else:
        resp = response.json()
        if (len(resp) == 0):
            #raise Exception("Lidarr can't find MB ID:", guid) 
            return None
        if (len(resp) > 1):
            raise Exception("Lidarr returned more than one rec for MB ID:", guid) 
        if ('artist' in resp[0]):
            return resp[0]['artist']
        if ('album' in resp[0]):
            return resp[0]['albumn']
        else:    
            raise Exception("Lidarr should have returned artist or album but returned something else for MB ID:", guid) 


def getSearchResults(album, artist):
    #print("Artist:" + artist + " Album:" + album + " Year:", year) #, end = '')
    #params = {'term': "{albumname:" + album + "}{artistName:" + artist + "}"}
    #params = {'term': album }
    # params = {'term': album + " - " + artist}
    
    params = {'term': album + " - " + artist}
    enc = urllib.parse.urlencode(params)
    requrl = prefix + "search?" + enc
    response = requests.get(requrl,  headers=requestheaders)
    if (response.status_code != 200):
        print("Error", response.status_code)
        raise Exception("API Error", response) 
    else:
        return response.json()

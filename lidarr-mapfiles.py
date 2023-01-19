import requests
import urllib.parse
import re
import difflib
import os

LIDARRAPIKEY = os.getenv('LIDARRAPIKEY')
LIDARRURL = os.getenv('LIDARRURL')
STRIPPATHPREFIX = os.getenv('STRIPPATHPREFIX')
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
response = requests.get(prefix + "trackFile?unmapped=true",  headers=requestheaders)

if (response.status_code != 200):
    print("Error", response.status_code)
else:
    #print(response.json())
    curalbum = 0
    keys = set()
    for album in response.json():
        curalbum +=1
        #print (album["path"])
        albumpath=album["path"].replace(STRIPPATHPREFIX,"")
        splits = albumpath.split("/")
        album = splits[1]
        artist = splits[0]
        key = album + " {album}: " + artist + " {artist}"
        if key not in keys:  #only process first track from each album
            keys.add(key)
            #album = "100 Essential Christmas Songs (2010)"
            #artist = "Various Artists"
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
            artist = artist.lower().strip()
            album = album.lower().replace(artist,"").strip()
            album = album.replace("(disc 1)","")
            album = album.replace("(disc 2)","")
            album = album.replace("(disc 3)","")
            album = album.replace("(disc 4)","")
            #print("Artist:" + artist + " Album:" + album + " Year:", year) #, end = '')
            #params = {'term': "{albumname:" + album + "}{artistName:" + artist + "}"}
            #params = {'term': album }
            params = {'term': album + " - " + artist}
            enc = urllib.parse.urlencode(params)
            requrl = prefix + "search?" + enc
            response = requests.get(requrl,  headers=requestheaders)
            curres = 0
            foundalbum = False        
            bestfoundalbum = None
            printedAlbum = False
            for searchres in response.json():
                if ("album" in searchres):
                    if ("id" in searchres["album"]):
                        #print("\tFound Imported Album:" +bestfoundalbum["title"] + " Artist: " + foundartist["artistName"] + " id:", bestfoundalbum["id"] )
                        break

            artistId = None
            for searchres in response.json():
                artistName=None
                curArtistId=None
                if ("artist" in searchres):
                    if ("id" in searchres["artist"]):
                        artistName = searchres["artist"]["artistName"]
                        curArtistId = searchres["artist"]["id"]
                if ("album" in searchres):
                        curArtistId = searchres["album"]["artist"]["id"]
                if (artistName is not None):
                    artistscore = difflib.SequenceMatcher(a=artistName.lower(), b=artist.lower())
                    if (artistscore.ratio() > 0.9):
                        artistId=int( curArtistId)                        
                    break

            if (artistId == None):
                break  #give up couldnt even find the artist
            for searchres in response.json():
                if ("album" in searchres):
                    foundalbum = True
                    bestfoundalbum = searchres["album"]
                    foundartist = bestfoundalbum["artist"]
                    if ("id" in bestfoundalbum):
                        #print("\tFound Imported Album:" +bestfoundalbum["title"] + " Artist: " + foundartist["artistName"] + " id:", bestfoundalbum["id"] )
                        break
                    if (foundartist["id"] != artistId):
                        break # artist doesnt match skip
                    else:
                        if (not printedAlbum):
                            print("Searching Unimported Artist:" + artist + " Album:" + album + " Year:", year, "Artist Id:", artistId) #, end = '')
                            printedAlbum = True
                        #print(" Checking UnImported Album:" +bestfoundalbum["title"] + " Artist: " + foundartist["artistName"] + " id:", bestfoundalbum["id"] )
                        artistscore =difflib.SequenceMatcher(a=foundartist["artistName"].lower(), b=artist.lower())
                        albumscore =difflib.SequenceMatcher(a=bestfoundalbum["title"].lower(), b=album.lower())
                        artistmatch = artistscore.ratio() > 0.7
                        albumMatch = albumscore.ratio() > 0.7
                        matchstr = ""
                        if (albumMatch and not artistmatch): matchstr ="**ALBUM MATCH** "
                        if (not albumMatch and artistmatch): matchstr ="**ARTIST MATCH** "
                        if (albumMatch and artistmatch): matchstr ="**MATCH** "
                        if (albumMatch and artistmatch):
                            print("Artist:" + artist + " Album:" + album + " Year:", year) #, end = '')
                            print("\t" + matchstr + "\tUnimported Album:" + bestfoundalbum["title"] + " Artist: " + foundartist["artistName"] + " Artist Score:",  artistscore.ratio(), " Album Score:", albumscore.ratio())
                        if (albumMatch and artistmatch):
                            print("*** ADDING ALBUM TO LIDARR ***")
                            bestfoundalbum["addOptions"] = { "searchForNewAlbum": False }
                            #" `"addOptions`":{`"searchForNewAlbum`":false}}"
                            #print(bestfoundalbum)
                            requrl = prefix + "album"
                            response = requests.post(requrl,  headers=requestheaders, json=bestfoundalbum)
                            if (not response.ok):
                                print("Error adding record ", response.reason)
                            else:
                                print(response.json())

                            break
                if (foundalbum):
                    curres +=1
                if (curres > 999):
                    break
            if (curalbum > 99999):
                break



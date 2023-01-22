import difflib

def findReleaseGroupInArtist(artist, album):
    album = album.strip().lower()
    for rgroup in artist["release-group-list"]:
        groupname = rgroup["title"]
        albumscore = difflib.SequenceMatcher(a=groupname.lower(), b=album)
        if (albumscore.ratio() > 0.9):
            return rgroup
    return None

def hasImportedResult(searchresults):
    for searchres in searchresults:
        if ("album" in searchres):
            if ("id" in searchres["album"]):
                #print("\tFound Imported Album:" +bestfoundalbum["title"] + " Artist: " + foundartist["artistName"] + " id:", bestfoundalbum["id"] )
                return True
    return False

def findArtistId(searchresults, artist):
    artistId = None
    artist = artist.lower()
    for searchres in searchresults:
        artistName=None
        curArtistId=None
        if ("artist" in searchres):
            if ("id" in searchres["artist"]):
                artistName = searchres["artist"]["artistName"]
                curArtistId = searchres["artist"]["id"]
        if ("album" in searchres):
                curArtistId = searchres["album"]["artist"]["id"]
        if (artistName is not None):
            artistscore = difflib.SequenceMatcher(a=artistName.lower(), b=artist)
            if (artistscore.ratio() > 0.9):
                artistId=int( curArtistId)                        
            break  
    return artistId  

def findArtistInCache(artists, artistName):
    #artistId = None
    foundArtist = None
    aname = artistName.strip().lower()
    for artist in artists:
        artistscore = difflib.SequenceMatcher(a=aname, b=artist["artistName"].lower())
        if (artistscore.ratio() > 0.9):
            #artistId=int(artist["id"])                
            foundArtist = artist
            break
    return foundArtist      

def rankAlbum(album):
    if (album is None):
        return 0
    else:        
        if (album["albumType"].lower() == "album"): # prefer albums
            return 100
        else:
            return 10

def goodAlbum(album):
    return (album["albumType"].lower() == "album")

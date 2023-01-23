import difflib
import os
import shutil
from pathlib import Path
import unicodedata
import mb
from datetime import datetime
from lidarrapi import getUnmappedFiles, getSearchResults, getArtists
from lidarrapi import getArtistAlbums,getSearchResultByGuid, addArtist, addAlbum
from filepath import getAlbumFromPath, getArtistFromPath, getYearFromPath, getAlbumNoParenFromPath, getLocalAlbumPathFromPath, getLocalFileFromPath, WinSafePath, renameFolder
from search import hasImportedResult, findArtistId, findArtistInCache, rankAlbum, goodAlbum, findReleaseGroupInArtist
import webbrowser

#rels=mb.getReleasesByReleaseGroupId("bac3876a-8d13-3a21-b94d-6a55144ae698")
#rels2=mb.getReleasesByReleaseGroupId("8f5f6bdf-5041-3312-94cb-3fb1daa710d0")

#lartist = getSearchResultByGuid('fa7466b4-1521-482a-94f3-81b3c8b5b0b3')
#lartist2= getSearchResultByGuid('debabff3-2559-46e5-862d-ef2a906d7010')

unmappedFiles = getUnmappedFiles()
print("Unmapped File Count:" + str(len(unmappedFiles)))
artists = getArtists()
ROOTFOLDERPATH = os.getenv('ROOTFOLDERPATH')
LOCALFOLDERPATH= os.getenv('LOCALFOLDERPATH')
MOVEUNKNOWNALBUMSTOSUBFOLDER= os.getenv('MOVEUNKNOWNALBUMSTOSUBFOLDER')
REMOVEM4AIFMP3= (os.getenv('REMOVEM4AIFMP3') == "True")
REMOVEWMAIFOTHER=  (os.getenv('REMOVEWMAIFOTHER') == "True")
REMOVEANYIFFLAC=  (os.getenv('REMOVEANYIFFLAC') == "True")
#somehow we get a triple backslash on the beginning
#LOCALFOLDERPATH = LOCALFOLDERPATH.replace("\\\\\\","\\\\")
curalbum = 0
albumKeys = set()
artistAlbums ={}

releaseKeys = set()
albumReleaseGroups = {}
#remove dupes
# for root, subdirs, files in os.walk(LOCALFOLDERPATH):
#     for filename in files:
#         file_path = os.path.join(root, filename)
#         removefile=False
#         localfileext= str(os.path.splitext(file_path)[1])
#         localfilenoext= str(os.path.splitext(file_path)[0])
#         ismp3 = (localfileext.lower() == ".mp3")
#         ism4a = (localfileext.lower() == ".m4a")
#         ism4p =  (localfileext.lower() == ".m4p") #lidarr doesn't like m4ps
#         iswav = (localfileext.lower() == ".wav")
#         iswma = (localfileext.lower() == ".wma")
#         isflac = (localfileext.lower() == ".flac")

#         hasmp3 = os.path.exists(localfilenoext + ".mp3")
#         hasm4a = os.path.exists(localfilenoext + ".m4a")
#         hasflac = os.path.exists(localfilenoext + ".flac")
#         haswma = os.path.exists(localfilenoext + ".wma")
#         haswav = os.path.exists(localfilenoext + ".wav")

#         removefile =(REMOVEANYIFFLAC and not isflac and hasflac) or  \
#                     (REMOVEWMAIFOTHER and (iswav or iswma) and (hasmp3 or hasm4a or hasflac)) or \
#                     (REMOVEM4AIFMP3 and (ism4a or ism4p) and hasmp3)
#         if (removefile):
#             print("Removing file:" + file_path + " because a better version exists")
#             os.remove(file_path)

for trackFile in unmappedFiles:
    curalbum +=1

    localfile = getLocalFileFromPath(trackFile["path"])

    if (not os.path.exists(localfile)):
        print("File does not exists you may need to have lidarr rescan:" + localfile)
    else:
        yearFromPath = getYearFromPath(trackFile["path"])
        artistNameFromPath = getArtistFromPath(trackFile["path"])
        albumNameFromPath = getAlbumFromPath(trackFile["path"])
        albumNameNoParen = getAlbumNoParenFromPath(trackFile["path"])
        albumPath = getLocalAlbumPathFromPath(trackFile["path"])
        if (albumNameNoParen.strip().lower() == "[unknown]"): 
            break
        key = albumNameFromPath + " {album}: " + artistNameFromPath + " {artist}"
        if key not in albumKeys:  #only process first track from each album
            albumKeys.add(key)
            #searchresults = getSearchResults(albumNameFromPath, artistNameFromPath)
            curres = 0
            bestfoundalbum = None

            artistRec =findArtistInCache(artists, artistNameFromPath)
            mbartist = None
            lartist = None
            foundartist = None

            if (artistRec is not None):
                foundartist = artistRec
            else:
                print("\t***ERROR ARTIST NOT FOUND** :" + artistNameFromPath + ", checking via musicbrainz")
                ## TODO: Search musicbrainz and add artist if found
                mbartist = mb.getArtist(artistNameFromPath)

                if (mbartist):
                    # check if this artist already added
                    lartist = getSearchResultByGuid(mbartist['id'])
                    if (lartist is not None):
                        if ('id' in lartist):
                            print("\t** found artist in lidarr under alias. artist=", lartist["artistName"])
                            frm = os.path.join(LOCALFOLDERPATH, artistNameFromPath)
                            to =  os.path.join(LOCALFOLDERPATH, lartist["artistName"])
                            #if (lartist["artistName"].lower() == artistNameFromPath.lower()):
                            #TODO: Better unicode
                            f1=unicodedata.normalize("NFKD", lartist["artistName"].lower()).encode('ascii', 'ignore').decode("utf-8").replace("-","")
                            f2=unicodedata.normalize("NFKD", artistNameFromPath.lower()).encode('ascii', 'ignore').decode("utf-8").replace("-","")
                            if (f1  == f2 ):
                                print("These two folders are same except for case.. you need to fix on server manually: " + str(frm) + ", " + str(to))
                            else:
                                print("Renaming artist folder from ", repr(frm), " to ", repr(to))
                                renameFolder(WinSafePath(frm), WinSafePath(to))
                                foundartist=lartist
                                artists.append(foundartist)
                        else:
                            print("\t** this artist found in MB but not lidarr, adding to lidarr **")
                            foundartist = addArtist(lartist)
                            artists.append(foundartist)


            if (foundartist is None):
                print("\t***Giving up, Unable to find artist in lidarr or MB** :" + artistNameFromPath)
                ## TODO: Search musicbrainz
                #artist = mb.getArtist(artistNameFromPath)
                # bestfoundalbum["addOptions"] = { "searchForNewAlbum": False }
                # #" `"addOptions`":{`"searchForNewAlbum`":false}}"
                # #print(bestfoundalbum)
                # requrl = prefix + "album"
                # response = requests.post(requrl,  headers=requestheaders, json=bestfoundalbum)
                # if (not response.ok):
                #     print("Error adding record ", response.reason)
                # else:
                #     print(response.json())

            else:
                artistId  =int(foundartist["id"])
                # cache api call
                if (artistId in artistAlbums):
                    albums=artistAlbums[artistId]
                else:
                    albums=getArtistAlbums(artistId)
                    artistAlbums[artistId]=albums

                renameto=None
                for album in albums:
                    if (rankAlbum(bestfoundalbum) < rankAlbum(album)):
                        albumscore =difflib.SequenceMatcher(a=album["title"].lower(), b=albumNameFromPath)
                        if (albumscore.ratio() > 0.9):
                            #print("**ALBUM found *** File Title:" + albumNameFromPath + " = Lidarr Title:" +album["title"].lower() + " ID=", album["id"])
                            bestfoundalbum=album
                            renameto=None
                            if (goodAlbum(album)): break
                        else:
                            # try again with () removed
                            albumscore =difflib.SequenceMatcher(a=album["title"].lower(), b=albumNameNoParen)
                            if (albumscore.ratio() > 0.9):
                                relyear = datetime.strptime(album['releaseDate'], '%Y-%m-%dT%H:%M:%SZ').strftime("%Y")
                                renameto = os.path.join(LOCALFOLDERPATH, artistNameFromPath , album["title"] + " (" + str(relyear) + ")")
                                #print("**ALBUM found *** File Title:" + albumNameFromPath + " = Lidarr Title:" +album["title"].lower() + " ID=", album["id"])
                                bestfoundalbum=album
                                if (goodAlbum(album)): break
                fullalbumpath =  os.path.join(LOCALFOLDERPATH, artistNameFromPath, albumNameFromPath)
                if (yearFromPath is not None and str(yearFromPath).strip() != ''):
                    fullalbumpath=fullalbumpath + " (" + str(yearFromPath) + ")"
                if (renameto is not None):
                    renamefrom= fullalbumpath
                    print("Merging album folder from ", repr(renamefrom), " to ", repr(renameto))
                    if (not os.path.exists(WinSafePath(renamefrom))):
                        print("Album folder does not exist.. refresh Lidarr:" + str(WinSafePath(renamefrom)))
                    else:
                        renameFolder(WinSafePath(renamefrom), WinSafePath(renameto))
                else:

                    if (bestfoundalbum is None):
                        print("\t**ALBUM not found *** Name From File:" + albumNameFromPath + " Artist From File:" + artistNameFromPath + " Lidarr Artist:" + foundartist["artistName"] + " Local file:" + localfile)

                        artistwithreleases = mb.getArtistAlbums(foundartist)
                        if (artistwithreleases is not None): foundartist=artistwithreleases
                        rg = findReleaseGroupInArtist(foundartist, albumNameFromPath)
                        if (rg is None): rg = findReleaseGroupInArtist(foundartist, albumNameNoParen)
                        if (rg is not None):
                            print("\t**Found Album in MB but not Lidarr id = lidarr:" + str(rg['id']))
                            album = getSearchResultByGuid(str(rg['id']))
                            if (album is not None):
                                album["addOptions"] = { "searchForNewAlbum": False }
                                bestfoundalbum=addAlbum(album)
                            else:
                                rels=mb.getReleasesByReleaseGroupId(rg['id'])
                                for rel in rels["release-list"]:
                                    if ("status" not in rel):
                                        print("\t**Found Release group with unknown releases.. popping up browser for user to set")
                                        # no documented api to update release... pop up browser for user to edit
                                        url = "https://musicbrainz.org/release/" + str(rel["id"] + "/edit")
                                        webbrowser.open(url, new=0, autoraise=True)
                        else:
                            searchresults = getSearchResults(albumNameFromPath, artistNameFromPath)
                            for searchres in searchresults:
                                if ("album" in searchres):
                                    foundalbum = True
                                    bestfoundalbum = searchres["album"]
                                    foundartist = bestfoundalbum["artist"]
                                    if ("id" in bestfoundalbum):
                                        #print("\tFound Imported Album:" +bestfoundalbum["title"] + " Artist: " + foundartist["artistName"] + " id:", bestfoundalbum["id"] )
                                        break
                                    if ("id" in foundartist and foundartist["id"] != artistId):
                                        break # artist doesnt match skip
                                    else:
                                        artistscore =difflib.SequenceMatcher(a=foundartist["artistName"].lower(), b=artistNameFromPath.lower())
                                        albumscore =difflib.SequenceMatcher(a=bestfoundalbum["title"].lower(), b=albumNameFromPath.lower())
                                        artistmatch = artistscore.ratio() > 0.7
                                        albumMatch = albumscore.ratio() > 0.7
                                        matchstr = ""
                                        if (artistmatch and albumMatch):
                                            bestfoundalbum["addOptions"] = { "searchForNewAlbum": False }
                                            print("Added album ", bestfoundalbum["title"])
                                            bestfoundalbum=addAlbum(bestfoundalbum)
                            #             if (albumMatch and not artistmatch): matchstr ="**ALBUM MATCH** "
                            #             if (not albumMatch and artistmatch): matchstr ="**ARTIST MATCH** "
                            #             if (albumMatch and artistmatch): matchstr ="**MATCH** "
                            #             if (albumMatch and artistmatch):
                            


                            # if (MOVEUNKNOWNALBUMSTOSUBFOLDER is not None and MOVEUNKNOWNALBUMSTOSUBFOLDER != ""):
                            #     ufolder = os.path.join(fullalbumpath, "..", MOVEUNKNOWNALBUMSTOSUBFOLDER)

                            #     if (MOVEUNKNOWNALBUMSTOSUBFOLDER not in fullalbumpath): # don't move twice
                            #         print("\tMOVING ALBUM TO " + ufolder + " SUBFOLDER")
                            #         if not os.path.exists(ufolder):
                            #             os.mkdir(ufolder)
                            #         shutil.move(fullalbumpath, ufolder)


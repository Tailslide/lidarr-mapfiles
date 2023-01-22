# Import the module
import musicbrainzngs
import os

MBUSER = os.getenv('MBUSER')
MBPASSWORD = os.getenv('MBPASSWORD')

# If you plan to submit data, authenticate
musicbrainzngs.auth(MBUSER, MBPASSWORD)

# Tell musicbrainz what your app is, and how to contact you
# (this step is required, as per the webservice access rules
# at http://wiki.musicbrainz.org/XML_Web_Service/Rate_Limiting )
musicbrainzngs.set_useragent("lidarr-mapfiles", "0.1", "https://github.com/Tailslide/lidarr-mapfiles")

# If you are connecting to a different server
musicbrainzngs.set_hostname("beta.musicbrainz.org")

def getArtist(aname):
    result = musicbrainzngs.search_artists(artist=aname,) #, type="group",country="GB")
    aname=aname.strip().lower()
    for artist in result['artist-list']:
        if (artist['name'].strip().lower() == aname):
            print(u"\t\t**FOUND MB ARTIST**{id}: {name}".format(id=artist['id'], name=artist["name"]))
            return artist
        else:
            if ('alias-list' in artist):
                for alias in artist['alias-list']:
                    if (alias['alias'].strip().lower() == aname):
                        print(u"\t\t**FOUND MB ARTIST under alias**{id}: {name}".format(id=artist['id'], name=artist["name"]))
                        return artist

def getArtistAlbums(artist):
    try:
       res= musicbrainzngs.get_artist_by_id(artist["foreignArtistId"], includes=["release-groups"], release_type=["album", "ep", "single"])
       return res["artist"]
    except Exception as err:
        print(f"Unexpected {err=}, {type(err)=}")
        raise

def getReleasesByReleaseGroupId(id):
    try:
       res= musicbrainzngs.get_release_group_by_id(id, includes=['releases'])
       return res["release-group"]
    except Exception as err:
        print(f"Unexpected {err=}, {type(err)=}")
        raise

musicbrainzngs.add_releases_to_collection
# getArtistRelaseGroups(album):
#    return musicbrainzngs.search_release_groups(arid=artist["id"]) 

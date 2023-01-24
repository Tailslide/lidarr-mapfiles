# lidarr-mapfiles
Tool to automatically map unmapped files in lidarr

DO NOT JUST RUN THIS.. this is a starting point for making your own scripts.
Make a copy of your library and backup lidarr in case it kills everything.

I followed these steps:

1. run musicbrainz picard on my disorganized folder to rename and organize my albums
2. sink into a depression looking at the long list of unmapped files left over in lidarr
3. mess around with the code bits here to get everything mapped up. You will have issues since Lidarr doesn't let you use releases with 'unknown' status or releases that include audio and video.. there is routine to pop up the musicbrainz website to edit release status.
4. Move all the classical artists into a different folder that lidarr doesn't monitor (lidarr doesn't handle classical music well)
5. Remove the classical artists manually

## Debugging

Make a .env file and put your secrets there:

```

LIDARRAPIKEY="asdfkjskdf12312312"
LIDARRURL="http://mylidarrserver:8686/api/v1/"
ROOTFOLDERPATH="/volume1/path/to/Music/"
MBUSER="mymusicbrainzuser"
MBPASSWORD="mymusicbrainzpassword"
MOVEUNKNOWNALBUMSTOSUBFOLDER="[UNKNOWN]"
REMOVEM4AIFMP3="True"
REMOVEWMAIFOTHER="True"
REMOVEANYIFFLAC="True"

```
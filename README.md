# lidarr-mapfiles
Tool to automatically map unmapped files in lidarr

DO NOT JUST RUN THIS.. this is a starting point for making your own scripts.
Make a copy of your library and backup lidarr in case it kills everything.

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
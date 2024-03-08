import xbmc
import time
import os
import shutil
import sys
import glob
from os import listdir
from shutil import copyfile
from shutil import rmtree
from datetime import datetime
from datetime import timedelta
import zipfile
import urllib
import base64 as b




 
#for XStream   

XstreamUpd = xbmc.translatePath('special://home/userdata/addon_data/plugin.video.xstream/update_sha')

if os.path.exists(XstreamUpd):
    try:
        os.remove(XstreamUpd)
    except:
        pass
 

#for Stalker

TVguideS1 = xbmc.translatePath('special://home/userdata/addon_data/pvr.stubebox.stalker/epg_xmltv.xml')

if os.path.exists(TVguideS1):
    try:
        os.remove(TVguideS1)
    except:
        pass


TVguideS2 = xbmc.translatePath('special://home/userdata/addon_data/pvr.stubebox.stalker/epg_provider.json')

if os.path.exists(TVguideS2):
    try:
        os.remove(TVguideS2)
    except:
        pass


TVguideS3 = xbmc.translatePath('special://home/userdata/Database/Epg12.db')

if os.path.exists(TVguideS3):
    try:
        os.remove(TVguideS3)
    except:
        pass



    
#!/usr/bin/python
# -*- coding: utf-8 -*-
import xbmcaddon,xbmcplugin,xbmcgui,urllib,sys,re,os,urlparse,urllib2

addon = xbmcaddon.Addon()
pluginhandle = int(sys.argv[1])
addonID = addon.getAddonInfo('id')
icon1=xbmc.translatePath('special://home/addons/'+addonID+'/vavootv.png')
icon2=xbmc.translatePath('special://home/addons/'+addonID+'/pluto.png')
icon4=xbmc.translatePath('special://home/addons/'+addonID+'/sms.png')
icon5=xbmc.translatePath('special://home/addons/'+addonID+'/m3u.png')
#icon6=xbmc.translatePath('special://home/addons/'+addonID+'/netzk.png')
icon7=xbmc.translatePath('special://home/addons/'+addonID+'/stb.png')
#icon8=xbmc.translatePath('special://home/addons/'+addonID+'/stube.png')
#icon9=xbmc.translatePath('special://home/addons/'+addonID+'/sgr.png')
icon11=xbmc.translatePath('special://home/addons/'+addonID+'/line.png')



def index():
    addDir("Stube~Live~De","plugin://plugin.video.vavooto/?action=channels",icon11)
    addDir("WORLD.LİVE","plugin://plugin.video.stubevavoo/?action=channels&type=channels",icon1)
    addDir("PLUTO.TV","plugin://slyguy.pluto.tv.provider/?_=live_tv",icon2)
    addDir("SAMSUNG.TV","plugin://slyguy.samsung.tv.plus/?_=live_tv",icon4)
    addDir("STALKER.TV","plugin://plugin.program.super.favourites/?cmd=ActivateWindow(TvChannels)&content_type&image=special%3a%2f%2fhome%2faddons%2fskin.stubeboxv4%2fmedia%2ficons%2fstb.png&label=%5bCOLOR%20ghostwhite%5dSTALKER%20%20LIVE%20TV%5b%2fCOLOR%5d&mode=650",icon7)
    addDir("M3U.PLAY","plugin://plugin.video.playlistLoader",icon5)


    xbmcplugin.endOfDirectory(pluginhandle)
    
    
    
def addDir(name,url,iconimage):
    ok=True
    liz=xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
    liz.setInfo( type="Video", infoLabels={ "Title": name } )
    liz.setProperty('fanart_image',iconimage)
    ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=url,listitem=liz,isFolder=True)
    return ok


def translation(id):
    return addon.getLocalizedString(id).encode('utf-8')


def parameters_string_to_dict(parameters):
    paramDict = {}
    if parameters:
        paramPairs = parameters[1:].split("&")
        for paramsPair in paramPairs:
            paramSplits = paramsPair.split('=')
            if (len(paramSplits)) == 2:
                paramDict[paramSplits[0]] = paramSplits[1]
    return paramDict

index()

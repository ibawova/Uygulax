#!/usr/bin/python
# -*- coding: utf-8 -*-
import xbmcaddon,xbmcplugin,xbmcgui,urllib,sys,re,os,urlparse,urllib2

addon = xbmcaddon.Addon()
pluginhandle = int(sys.argv[1])
addonID = addon.getAddonInfo('id')
icon1=xbmc.translatePath('special://home/addons/'+addonID+'/xl.png')
icon2=xbmc.translatePath('special://home/addons/'+addonID+'/xl.png')
#icon3=xbmc.translatePath('special://home/addons/'+addonID+'/utm.png')
#icon4=xbmc.translatePath('special://home/addons/'+addonID+'/bums.png')
icon5=xbmc.translatePath('special://home/addons/'+addonID+'/xl.png')
#icon6=xbmc.translatePath('special://home/addons/'+addonID+'/jfh.png')
#icon7=xbmc.translatePath('special://home/addons/'+addonID+'/sxra.png')

def index():
    addDir("Videodevil","plugin://plugin.video.videodevil",icon1)
    addDir("Cumination","plugin://plugin.video.cumination",icon2)
    #addDir("Ultimate Whitecream","plugin://plugin.video.uwc",icon3)
    #addDir("BumsFilme","plugin://plugin.video.bumsfilme",icon4)
    addDir("Invocom","plugin://plugin.video.invocom",icon5)
    #addDir("Just For Him","plugin://plugin.video.jfh",icon6)
    #addDir("Sexuria.com","plugin://plugin.video.sexuria.com",icon7)
       
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

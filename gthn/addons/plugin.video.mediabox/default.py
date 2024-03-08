#!/usr/bin/python
# -*- coding: utf-8 -*-
import xbmcaddon,xbmcplugin,xbmcgui,urllib,sys,re,os,urlparse,urllib2

addon = xbmcaddon.Addon()
pluginhandle = int(sys.argv[1])
addonID = addon.getAddonInfo('id')
icon1=xbmc.translatePath('special://home/addons/'+addonID+'/xstream.png')
icon2=xbmc.translatePath('special://home/addons/'+addonID+'/doku.png')
icon4=xbmc.translatePath('special://home/addons/'+addonID+'/ilr.png')
icon5=xbmc.translatePath('special://home/addons/'+addonID+'/music.png')
icon6=xbmc.translatePath('special://home/addons/'+addonID+'/you.png')
icon7=xbmc.translatePath('special://home/addons/'+addonID+'/tvnow.png')
icon8=xbmc.translatePath('special://home/addons/'+addonID+'/xship.png')
icon9=xbmc.translatePath('special://home/addons/'+addonID+'/joyn.png')
icon10=xbmc.translatePath('special://home/addons/'+addonID+'/disney.png')
icon11=xbmc.translatePath('special://home/addons/'+addonID+'/vavooF.png')
icon12=xbmc.translatePath('special://home/addons/'+addonID+'/vavooS.png')


def index():
    addDir("X.STREAM","plugin://plugin.video.xstream",icon1)
    addDir("VAVOO.FILME","plugin://plugin.video.vavooto/indexMovie?action=indexMovie&amp;cancel=home",icon11)
    addDir("VAVOO.SERIEN","plugin://plugin.video.vavooto/?action=indexSerie&amp;cancel=home",icon12)
    addDir("X.SHİP","plugin://plugin.video.xship",icon8)
    addDir("HOMELANDER","plugin://plugin.video.homelander",icon2)
    addDir("DISNEY+","plugin://slyguy.disney.plus",icon10)
    #addDir("TV.NOW","plugin://plugin.video.tvnow.de",icon7)
    #addDir("JOYN","plugin://plugin.video.joyn",icon9)
    addDir("I.LOVE.RADIO","plugin://plugin.audio.iloveradio",icon4)
    #addDir("TIDE","plugin://plugin.video.tide",icon9)
    addDir("YOU.TUBE","plugin://plugin.video.youtube",icon6)

   

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

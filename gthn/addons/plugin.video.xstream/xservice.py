# -*- coding: utf-8 -*-
#
# 2022-06-21 Heptamer - Änderung siehe Zeile 72ff
#
import sys, os, json, re, xbmc, xbmcaddon, xbmcgui
from xbmc import LOGDEBUG, LOGERROR

AddonName = xbmcaddon.Addon().getAddonInfo('name')
# xbmcaddon.Addon().getAddonInfo('id')

if sys.version_info[0] == 2:
    from xbmc import translatePath
    NIGHTLY_VERSION_CONTROL = os.path.join(translatePath(xbmcaddon.Addon().getAddonInfo('profile')).decode('utf-8'), "update_sha")
    ADDON_PATH = translatePath(os.path.join('special://home/addons/', '%s')).decode('utf-8')
else:
    from xbmcvfs import translatePath
    NIGHTLY_VERSION_CONTROL = os.path.join(translatePath(xbmcaddon.Addon().getAddonInfo('profile')), "update_sha")
    ADDON_PATH = translatePath(os.path.join('special://home/addons/', '%s'))


def infoDialog(message, heading=AddonName, icon='', time=5000, sound=False):
    if icon == '': icon = xbmcaddon.Addon().getAddonInfo('icon')
    elif icon == 'INFO': icon = xbmcgui.NOTIFICATION_INFO
    elif icon == 'WARNING': icon = xbmcgui.NOTIFICATION_WARNING
    elif icon == 'ERROR': icon = xbmcgui.NOTIFICATION_ERROR
    xbmcgui.Dialog().notification(heading, message, icon, time, sound=sound)

def enableAddon(ADDONID):
    struktur = json.loads(xbmc.executeJSONRPC('{"jsonrpc":"2.0","method":"Addons.GetAddonDetails","id":1,"params": {"addonid":"%s", "properties": ["enabled"]}}' % ADDONID))
    if 'error' in struktur or struktur["result"]["addon"]["enabled"] != True:
        count = 0
        while True:
            if count == 5: break
            count += 1
            xbmc.executebuiltin('EnableAddon(%s)' % (ADDONID))
            xbmc.executebuiltin('SendClick(11)')
            xbmc.executeJSONRPC('{"jsonrpc":"2.0","method":"Addons.SetAddonEnabled","id":1,"params":{"addonid":"%s", "enabled":true}}' % ADDONID)
            xbmc.sleep(500)
            try:
                struktur = json.loads(xbmc.executeJSONRPC('{"jsonrpc":"2.0","method":"Addons.GetAddonDetails","id":1,"params": {"addonid":"%s", "properties": ["enabled"]}}' % ADDONID))
                if struktur["result"]["addon"]["enabled"] == True: break
            except:
                pass


def checkDependence(ADDONID):
    isdebug = True
    if isdebug: xbmc.log(__name__ + ' - %s - checkDependence ' % ADDONID, xbmc.LOGDEBUG)
    try:
        addon_xml = os.path.join(ADDON_PATH % ADDONID, 'addon.xml')
        with open(addon_xml, 'rb') as f:
            xml = f.read()
        pattern = '(import.*?addon[^/]+)'
        allDependence = re.findall(pattern, str(xml))
        #if isdebug: log_utils.log(__name__ + '%s - allDependence ' % str(allDependence), log_utils.LOGDEBUG)
        for i in allDependence:
            try:
                if 'optional' in i or 'xbmc.python' in i: continue
                pattern = 'import.*?"([^"]+)'
                IDdoADDON = re.search(pattern, i).group(1)
                if os.path.exists(ADDON_PATH % IDdoADDON) == True and xbmcaddon.Addon().getSetting('enforceUpdate') != 'true':
                    enableAddon(IDdoADDON)
                else:
                    xbmc.executebuiltin('InstallAddon(%s)' % (IDdoADDON))
                    xbmc.executebuiltin('SendClick(11)')
                    enableAddon(IDdoADDON)
            except:
                pass
    except Exception as e:
        xbmc.log(__name__ + '  %s - Exception ' % e, LOGERROR)
# Abfrage xStream Auto Update
if os.path.isfile(NIGHTLY_VERSION_CONTROL) == False or xbmcaddon.Addon().getSetting('githubUpdateXstream') == 'true'  or xbmcaddon.Addon().getSetting('enforceUpdate') == 'true':
    from resources.lib import updateManager
    status1 = updateManager.xStreamUpdate(True)
    # xStream Status Update
    infoDialog("Suche nach Updates ...", sound=False, icon='INFO', time=10000)
    if status1 == True: infoDialog('xStream Update erfolgreich installiert.', sound=False, icon='INFO', time=6000)
    if status1 == False: infoDialog('xStream Update mit Fehlern beendet.', sound=True, icon='ERROR')
    if status1 == None: infoDialog('Kein xStream Update verfügbar.', sound=False, icon='INFO', time=6000) 
# Abfrage Resolver Auto Update    
if os.path.isfile(NIGHTLY_VERSION_CONTROL) == False or xbmcaddon.Addon().getSetting('githubUpdateResolver') == 'true'  or xbmcaddon.Addon().getSetting('enforceUpdate') == 'true': 
    from resources.lib import updateManager
    status2 = updateManager.resolverUpdate(True)
    # Resolver Status Update    
    infoDialog("Suche nach Updates ...", sound=False, icon='INFO', time=10000)
    if status2 == True: infoDialog('Resolver ' + xbmcaddon.Addon().getSetting('resolver.branch') + ' Update erfolgreich installiert.', sound=False, icon='INFO', time=6000)
    if status2 == False: infoDialog('Resolver Update mit Fehlern beendet.', sound=True, icon='ERROR')
    if status2 == None: infoDialog('Kein Resolver Update verfügbar.', sound=False, icon='INFO', time=6000)
    if xbmcaddon.Addon().getSetting('enforceUpdate') == 'true': xbmcaddon.Addon().setSetting('enforceUpdate', 'false')

# "setting.xml" wenn notwendig Indexseiten aktualisieren
try:
    if xbmcaddon.Addon().getSetting('newSetting') == 'true':
        from resources.lib.handler.pluginHandler import cPluginHandler
        cPluginHandler().getAvailablePlugins()
except Exception:
    pass

checkDependence('plugin.video.xstream')

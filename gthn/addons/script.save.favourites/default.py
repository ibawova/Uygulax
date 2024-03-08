import xbmc
import os
import xbmcaddon
import xbmcgui
import xbmc
import threading


__addon__ = xbmcaddon.Addon()
addon = xbmcaddon.Addon
addon_id = 'script.save.favourites'
addonInfo = xbmcaddon.Addon().getAddonInfo
setting = xbmcaddon.Addon().getSetting
dialog = xbmcgui.Dialog()
setSetting = xbmcaddon.Addon().setSetting
execute = xbmc.executebuiltin


WINDOW_HOME = xbmcgui.Window(10000)

def get(key):
    return WINDOW_HOME.getProperty('Vavoo_' + key)


def set(key, value):
    if value is None:
        WINDOW_HOME.clearProperty('Vavoo_' + key)
    else:
        WINDOW_HOME.setProperty('Vavoo_' + key, value)
    return

def isVavooDevice():
    if xbmc.getCondVisibility('system.platform.android'):
        try:
            with open('/system/build.prop', 'r') as f:
                content = f.read()
            if 'ro.product.brand=VAVOO' in content and 'ro.vavoo.type=b' in content:
                return True
        except Exception:
            pass

    return False


def getPlatformName():
    if isVavooDevice():
        return 'android'
    elif xbmc.getCondVisibility('system.platform.android'):
        return 'android'
    elif xbmc.getCondVisibility('system.platform.linux'):
        return 'linux'
    elif xbmc.getCondVisibility('system.platform.windows'):
        return 'win32'
    elif xbmc.getCondVisibility('system.platform.osx'):
        return 'osx'
    elif xbmc.getCondVisibility('system.platform.ios'):
        return 'ios'
    elif xbmc.getCondVisibility('system.platform.atv2'):
        return 'atv2'
    else:
        return 'unknown'


def openSettings(query=None, id=addonInfo('id')):
    try:
        execute('Addon.OpenSettings(%s)' % id)
        dialog.ok('FAVORITEN','Lege zuerst den Speicherort deiner Favoriten fest.','Weiter mit OK.','Anschliessend Addon neu starten')
        xbmc.sleep(3000)
    except:
        pass

def openSettings1(query=None, id=addonInfo('id')):
    try:
        execute('Addon.OpenSettings(%s)' % id)
        dialog.ok('FAVORITEN','Bitte gebe den Wiederherstellungspfad deiner Favoriten an.','Weiter mit OK.','Anschliessend Addon neu starten')
        xbmc.sleep(3000)
    except:
        pass



def main():

        favourites = xbmc.translatePath('special://home/userdata/favourites.xml').decode('utf-8')
        platform = getPlatformName()
        dialog = xbmcgui.Dialog()
        entries = ["Favoriten sichern", "Favoriten wiederherstellen", None]

        nr = xbmcgui.Dialog().select("FAVORITEN", entries)
        entry = entries[nr]

        if entry == 'Favoriten sichern':
            if setting('speicher_pfad') == '':
                openSettings('0.0')
            else:
                Pfad = xbmc.translatePath(__addon__.getSetting('speicher_pfad')).decode('utf-8')
                if getPlatformName() == 'win32':
                    if not Pfad.endswith('\\'):
                        Pfad += '\\'
                else:
                    if not Pfad.endswith('/'):
                        Pfad += '/'
                FullPfad = Pfad + 'favourites.bak'
                if os.path.exists(favourites):
                    with open(favourites, 'r') as h:
                        reading = h.read()
                        with open(FullPfad, 'w') as g:
                            g.write(reading)
                    dialog.ok('FAVORITEN','Favoriten erfolgreich unter ',FullPfad , 'gespeichert')
                else:
                    dialog.ok('FAVORITEN','Du hast keine Favoriten angelegt','Weiter mit OK','')

        if entry == 'Favoriten wiederherstellen':
            Pfad = xbmc.translatePath(__addon__.getSetting('speicher_pfad')).decode('utf-8')
            if getPlatformName() == 'win32':
                if not Pfad.endswith('\\'):
                    Pfad += '\\'
            else:
                if not Pfad.endswith('/'):
                    Pfad += '/'
            FullPfad = Pfad + 'favourites.bak'
            FullPfadR = xbmc.translatePath(FullPfad).decode('utf-8')
            if os.path.exists(FullPfadR):
                with open(FullPfadR, 'r') as h:
                    reading = h.read()
                with open(favourites, 'w') as g:
                    g.write(reading)
                dialog.ok('FAVORITEN','Favoriten erfolgreich unter ',favourites , 'wiederhergestellt')
            else:
                if setting('re_pfad') == '':
                    openSettings1('0.2')
                else:
                    Pfad = xbmc.translatePath(__addon__.getSetting('re_pfad')).decode('utf-8')
                    with open(Pfad, 'r') as h:
                        reading = h.read()
                        with open(favourites, 'w') as g:
                            g.write(reading)
                    dialog.ok('FAVORITEN','Favoriten erfolgreich unter ',favourites , 'wiederhergestellt')




if __name__ == '__main__':
    main()
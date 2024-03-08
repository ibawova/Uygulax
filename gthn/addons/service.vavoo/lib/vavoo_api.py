# uncompyle6 version 3.7.4
# Python bytecode 2.7 (62211)
# Decompiled from: Python 2.7.17 (default, Sep 30 2020, 13:38:04) 
# [GCC 7.5.0]
# Embedded file name: /data/build/addons/service.vavoo/lib/vavoo_api.py
# Compiled at: 2018-10-03 02:01:50


def hasToken():
    import login
    if login.session.getToken():
        return True
    return False


def getToken():
    import login
    token = login.session.getToken()
    if not token:
        raise ValueError('Token is not set')
    return token


def userMode():
    import login
    token = getToken()
    if token == login.session.getGuestToken():
        return 'guest'
    return 'user'


def restart(rebootSystem=True):
    import variables, os, xbmcgui, xbmc
    try:
        from shlex import quote
    except ImportError:
        from pipes import quote

    platform = variables.getPlatformName()
    if platform == 'vavoo':
        xbmc.log('Using VAVOO restart method for system.platform.android')
        if rebootSystem:
            xbmc.executebuiltin('StartAndroidActivity(tv.vavoo.base!.RebootActivity)')
        else:
            xbmc.executebuiltin('XBMC.Quit()')
        return
    if platform == 'android':
        xbmc.log('Using builtin restart method for system.platform.android')
        p = xbmc.translatePath('special://home/_restart').decode('utf-8')
        with open(p, 'w') as (f):
            f.write('restart')
        xbmc.executebuiltin('XBMC.Quit()')
        return
    if platform == 'linux':
        content = ('#!/bin/sh\nwhile true ; do\n    pgrep vavoo.bin >/dev/null || break\n    i=$((i + 1))\n    [ $i -ge 2 ] && break\n    echo "Waiting for app exit #$i"\n    sleep 1\ndone\nkillall vavoo.bin 2>/dev/null\nkillall -9 vavoo.bin 2>/dev/null\n{APP}\nrm -f "$0"\n').replace('{APP}', os.environ.get('_', 'vavoo.bin'))
        p = xbmc.translatePath('special://home/_restart.sh').decode('utf-8')
        with open(p, 'w') as (f):
            f.write(content)
        os.system('sh ' + quote(p) + ' &')
        xbmc.executebuiltin('XBMC.Quit()')
        return
    if platform == 'osx':
        content = '#!/bin/sh\nwhile true ; do\n    pgrep VAVOO >/dev/null || break\n    i=$((i + 1))\n    [ $i -ge 2 ] && break\n    echo "Waiting for app exit #$i"\n    sleep 1\ndone\nkillall VAVOO 2>/dev/null\nkillall -9 VAVOO 2>/dev/null\nopen /Applications/VAVOO.app\nrm -f "$0"\n'
        p = xbmc.translatePath('special://home/_restart.sh').decode('utf-8')
        with open(p, 'w') as (f):
            f.write(content)
            os.system('sh ' + quote(p) + ' &')
        xbmc.executebuiltin('XBMC.Quit()')
        return
    if platform == 'ios':
        xbmc.log('Using default restart method for system.platform.ios')
    elif platform == 'win32':
        import subprocess
        xbmc.log('Using default restart method for system.platform.windows')
        content = '\nDim WshShell\nWScript.Sleep 5000\nSet WshShell = WScript.CreateObject("WScript.Shell")\nWshShell.Run "taskkill /F /T /IM vavoo.exe", 0, True\nWScript.Sleep 3000\nWshShell.Run """%LOCALAPPDATA%\\VAVOO\\vavoo.exe"""\n'
        p = xbmc.translatePath('special://home/_restart.vbs').decode('utf-8')
        with open(p, 'w') as (f):
            f.write(content)
        subprocess.Popen(['WScript.exe', p])
        xbmc.executebuiltin('XBMC.Quit()')
    elif platform == 'atv2':
        xbmc.log('Using default restart method for system.platform.atv2')
    else:
        xbmc.log('Unknown system, using default restart method')
    xbmcgui.Dialog().ok(heading=variables.localize(39577), line1=variables.localize(39578), line2=variables.localize(39579))
    xbmc.executebuiltin('XBMC.Quit()')


def hasInternet():
    import internet
    return internet.isConnected()


def waitForInternet():
    import internet
    internet.wait()


def hasBrowser():
    import xbmc, variables
    platform = variables.getPlatformName()
    if platform == 'android':
        try:
            import api
            if api.getSystemInfos().get('ro.product.manufacturer', None) == 'Amazon':
                return False
            return True
        except Exception as e:
            xbmc.log('Failed getting android installer: %s' % e, xbmc.LOGERROR)
            return False

    else:
        if platform in ('linux', 'win32', 'osx'):
            return True
        else:
            return False

    return


def openBrowser(link):
    import os, xbmc, variables
    platform = variables.getPlatformName()
    if platform in ('vavoo', 'android'):
        xbmc.executebuiltin('StartAndroidActivity(,android.intent.action.VIEW,,' + link + ')')
    elif platform == 'linux':
        os.system("sensible-browser '" + link + "' &")
    elif platform == 'win32':
        os.system('explorer "' + link + '"')
    elif platform == 'osx':
        os.system("open '" + link + "'")
    else:
        return False
    return True


def startGooglePay(sku):
    if userMode() == 'guest':
        import login
        login.session.runScript('login')
    else:
        import socket
        s = socket.socket()
        s.connect(('127.0.0.1', 35937))
        s.sendall(sku + '\n')
        s.sendall(getToken() + '\n')
        s.close()


def getAuthSignature(_retry=False):
    import variables
    signed = variables.WINDOW_HOME.getProperty('Vavoo_Signed')
    if not signed:
        signed = variables.addon.getSetting('signed')
    if not signed:
        if not _retry:
            raise ValueError('Failed getting signature')
        import login
        login.session.ping(reason='auth_signature')
        return getAuthSignature(True)
    return signed
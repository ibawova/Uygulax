# Embedded file name: /data/build/addons/service.vavoo/lib/vavoo_api.py

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


def restart(rebootSystem = True):
    import variables
    import os
    import xbmcgui
    import xbmc
    try:
        from shlex import quote
    except ImportError:
        from pipes import quote

    platform = variables.getPlatformName()
    if platform == 'android':
        xbmc.log('Using VAVOO restart method for system.platform.android')
        if rebootSystem:
            xbmc.executebuiltin('StartAndroidActivity(tv.vavoo.base!.RebootActivity)')
        else:
            xbmc.executebuiltin('XBMC.Quit()')
        return
	### in the next line: android to android
    if platform == 'android':
        xbmc.log('Using builtin restart method for system.platform.android')
        p = xbmc.translatePath('special://home/_restart').decode('utf-8')
        with open(p, 'w') as f:
            f.write('restart')
        xbmc.executebuiltin('XBMC.Quit()')
        return
    if platform == 'linux':
        content = '#!/bin/sh\nwhile true ; do\n    pgrep vavoo.bin >/dev/null || break\n    i=$((i + 1))\n    [ $i -ge 2 ] && break\n    echo "Waiting for app exit #$i"\n    sleep 1\ndone\nkillall vavoo.bin 2>/dev/null\nkillall -9 vavoo.bin 2>/dev/null\n{APP}\nrm -f "$0"\n'.replace('{APP}', os.environ.get('_', 'vavoo.bin'))
        p = xbmc.translatePath('special://home/_restart.sh').decode('utf-8')
        with open(p, 'w') as f:
            f.write(content)
        os.system('sh ' + quote(p) + ' &')
        xbmc.executebuiltin('XBMC.Quit()')
        return
    if platform == 'osx':
        content = '#!/bin/sh\nwhile true ; do\n    pgrep VAVOO >/dev/null || break\n    i=$((i + 1))\n    [ $i -ge 2 ] && break\n    echo "Waiting for app exit #$i"\n    sleep 1\ndone\nkillall VAVOO 2>/dev/null\nkillall -9 VAVOO 2>/dev/null\nopen /Applications/VAVOO.app\nrm -f "$0"\n'
        p = xbmc.translatePath('special://home/_restart.sh').decode('utf-8')
        with open(p, 'w') as f:
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
        with open(p, 'w') as f:
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
    import xbmc
    import variables
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
        return False
    return


def openBrowser(link):
    import os
    import xbmc
    import variables
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


def getAuthSignature(_retry = False):
    try:
        monitor = xbmc.Monitor()
        t = 0.0
        token = ''
        data = { }
        signed=''

        while not monitor.abortRequested():
            if time() > t:
                if control.getcache("plugin.video.vavooto.token") != '':
                    token = control.getcache("plugin.video.vavooto.token")

                data['ro.product.manufacturer'] =  'Amlogic'
                data['start_time'] = int(time() * 1000)
                data['ro.build.product'] = 'p212_6255'
                data['reason'] = 'check'
                data['apk_id'] = '475ece19d680ee7a812f110a84a21c69b55b6586'
                data['apk_package'] = 'org.xbmc.vavoo'
                data['is_playing'] = '0'
                data['current_time'] = int(time() * 1000)
                data['uptime'] = data['current_time'] - data['start_time']
                data['ro.build.version.release'] = '6.0.1'
                data['android_package_name'] = 'UNKNOWN'
                data['service_version'] = '1.2.26'
                data['apk_sha1'] = '475ece19d680ee7a812f110a84a21c69b55b6586'
                data['meta_system'] = 'Linux'
                data['apk_file'] = 'CERT.RSA'
                data['platform'] = 'vavoo'
                data['version'] = '2.2'
                data['branch'] = 'master'
                data['android_installer'] = 'com.android.packageinstaller'
                data['meta_version'] = ''
                data['recovery_version'] = '1.1.13'
                data['processor'] = ''

                if token != '':
                    signed = token
                else:
                    params = str.encode(vjson.dumps(data))
                    req = urllib.request.Request('https://www.vavoo.tv/api/box/guest', data=params, headers={'User-Agent': 'Mozilla/5.0 Cast/1.0'})
                    req.add_header('Content-Type', 'application/json; charset=utf-8')
                    response = urllib.request.urlopen(req)
                    json = vjson.loads(response.read().decode('utf8'))
                    if not json:
                        raise ValueError('Got no token!\n')
                    data['token'] = json.get('response', {}).get('token')
                    control.setcache( "plugin.video.vavooto.token", data['token'])
                    params = str.encode(vjson.dumps(data))
                    url1 = 'https://www.vavoo.tv/api/box/ping2'
                    req = requests.post(url1, data=data).json()
                    xbmcgui.Dialog().ok("Hashlib Generator ", str(req))
                    signed = req['response'].get('signed')
                signed = base64.b64decode(signed).decode('utf8')
                signed = signed.replace('false','true')
                signed = signed.replace('verified\\":true','verified\\":false')
                signed = signed.replace(':16', ':26')
                signed = signed.replace('3.', '4.')
                signed = signed.replace('5.', '6.')
                signed = signed.replace('7.', '8.')
                signed = signed.replace('9.', '0.')
                signed = base64.b64encode(str.encode(signed)).decode("utf-8")

                control.setcache( "plugin.video.vavooto.token", signed)
                t = time() + 1750
            xbmc.sleep(1000)
            return signed#control.getcache( "plugin.video.vavooto.token")

    except Exception as e:
        xbmc.log('ERROR: %r' % e)
        raise
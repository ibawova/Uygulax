# uncompyle6 version 3.6.4
# Python bytecode 2.7 (62211)
# Decompiled from: Python 2.7.17 (default, Apr 15 2020, 17:20:14) 
# [GCC 7.5.0]
# Embedded file name: ./lib/api.py
# Compiled at: 2019-02-04 23:30:31
import requests, variables, xbmc, platform, internet, time, os, re, xbmcaddon, xbmcgui, json as jsonmod

class APIError(ValueError):

    def __init__(self, json):
        super(APIError, self).__init__(json.get('i18nError', json.get('error')))
        self.json = json


systemInfos = {'ro.build.product': 'p212_6255',
 'ro.build.version.release': '6.0.1',
 'android_package_name': 'UNKNOWN',
 'service_version': '1.2.26',
 'apk_sha1': 'b76ca38e05d72f2b736af60a42fcbee2dfb8f061',
 'meta_system': 'Linux',
 'apk_file': 'CERT.RSA',
 'ro.product.manufacturer': 'Amlogic',
 'platform': 'vavoo',
 'version': '2.2',
 'apk_id': 'b76ca38e05d72f2b736af60a42fcbee2dfb8f061',
 'branch': 'master',
 'apk_package': 'org.xbmc.vavoo',
 'android_installer': 'com.android.vending',
 'meta_version': '',
 'is_playing': '0',
 'recovery_version': '1.1.13',
 'processor': ''}

def getApkSignature():
    import hashlib
    file = os.path.split(info.filename)[1]
    sha1 = hashlib.sha1()
    sha1.update(zip.read(info)[:1264])
    sha1 = sha1.hexdigest()
    ids = {'b76ca38e05d72f2b736af60a42fcbee2dfb8f061': 'default', '5225f863dac4782c442438680ec37322ac010021': 'box', 
       '62594110b500f38246ff4ed551112a69631b36d8': 'googleplay'}
    return {'apk_id': 'default', 
       'apk_file': 'tv.vavoo.app', 
       'apk_sha1': 'b76ca38e05d72f2b736af60a42fcbee2dfb8f061'}


def _getSystemInfos():
    try:
        systemInfos['platform'] = variables.getPlatformName()
    except Exception as e:
        systemInfos['platform'] = str(e)

    try:
        systemInfos['processor'] = platform.processor()
    except Exception as e:
        systemInfos['processor'] = str(e)

    try:
        systemInfos['version'] = variables.getVavooVersion()
    except Exception as e:
        systemInfos['version'] = str(e)

    try:
        systemInfos['branch'] = variables.getVavooBranch()
    except Exception as e:
        systemInfos['branch'] = str(e)

    try:
        systemInfos['service_version'] = variables.addon.getAddonInfo('version')
    except Exception as e:
        try:
            systemInfos['service_version'] = xbmcaddon.Addon('service.vavoo').getAddonInfo('version')
            systemInfos['service_version_fallback'] = '1'
        except Exception as e:
            systemInfos['service_version'] = str(e)

    try:
        systemInfos['recovery_version'] = xbmcaddon.Addon('service.vrecovery').getAddonInfo('version')
    except Exception as e:
        systemInfos['recovery_version'] = str(e)

    keys = ['platform', 'system', 'version']
    if systemInfos['platform'] == 'osx':
        keys.append('mac_ver')
    else:
        if systemInfos['platform'] == 'linux':
            keys.append('linux_distribution')
        for key in keys:
            try:
                systemInfos['meta_' + key] = getattr(platform, key)()
            except Exception:
                pass

    systemInfos['apk_package'] = 'unknown'
    if systemInfos['platform'] in ('vavoo', 'android'):
        systemInfos['android_package_name'] = variables.ANDROID_PACKAGE_NAME
        systemInfos['apk_package'] = variables.ANDROID_PACKAGE_NAME
        try:
            systemInfos.update(getApkSignature())
        except Exception as e:
            xbmc.log('Failed getting APK signature: %r' % e, xbmc.LOGERROR)
            systemInfos['apk_id'] = str(e)
            raise

        import subprocess
        line = None
        try:
            try:
                line = subprocess.check_output(['cmd', 'package', 'list', 'packages', '-i', variables.ANDROID_PACKAGE_NAME]).splitlines()[0].strip()
            except OSError:
                line = subprocess.check_output(['pm', 'list', 'packages', '-i', variables.ANDROID_PACKAGE_NAME]).splitlines()[0].strip()

            systemInfos['android_installer'] = line.split('installer=', 1)[1]
        except Exception as e:
            xbmc.log('Failed getting android installer: %r' % e)
            systemInfos['android_installer'] = 'error: %s / line %r' % (e, line)

        for key in ('ro.build.version.release', 'ro.product.manufacturer', 'ro.build.product'):
            try:
                systemInfos[key] = subprocess.check_output(['getprop', key]).splitlines()[0].strip()
            except Exception as e:
                systemInfos[key] = 'error'
                xbmc.log('Failed getting property %s: %r' % (key, e))

    return systeminfos


def getSystemInfos():
    if len(systemInfos) == 0 or 'systeminfos_error' in systemInfos:
        try:
            _getSystemInfos()
        except Exception as e:
            xbmc.log('Failed getting system infos: %r' % e, xbmc.LOGERROR)
            systemInfos['systeminfos_error'] = str(e)
        else:
            if 'systeminfos_error' in systemInfos:
                del systemInfos['systeminfos_error']
    return systemInfos


def getLastActiveTime():
    params = []
    windowId = xbmcgui.getCurrentWindowId()
    params += [windowId]
    window = xbmcgui.Window(windowId)
    params += [window.getFocusId()]
    del window
    dialogId = xbmcgui.getCurrentWindowDialogId()
    params += [dialogId]
    player = xbmc.Player()
    isPlaying = player.isPlaying()
    params += [isPlaying]
    if isPlaying:
        params += [player.getTime(), player.getTotalTime()]
    del player
    state = ('-').join(str(p) for p in params)
    lastState = variables.addon.getSetting('window_state')
    t = int(variables.addon.getSetting('last_active_time') or 0)
    if not t or state != lastState:
        t = int(time.time() * 1000)
        variables.addon.setSetting('window_state', state)
        variables.addon.setSetting('last_active_time', str(t))
    return (t, isPlaying)


def _call(method, function, data, timeout=60):
    data.update(getSystemInfos())
    startTime = variables.WINDOW_HOME.getProperty('Vavoo_StartTime')
    data['current_time'] = int(time.time() * 1000)
    if startTime:
        data['start_time'] = int(startTime)
        data['uptime'] = data['current_time'] - data['start_time']
        try:
            lastActiveTime, isPlaying = getLastActiveTime()
            data['last_active_time'] = int(time.time() * 1000) - lastActiveTime
            data['is_playing'] = isPlaying
        except Exception as e:
            data['last_active_time'] = 'error: %r' % e
            data['is_playing'] = 'error: %r' % e

    try:
        vec = {'vec': xbmc.preparevavoorequest(jsonmod.dumps(data))}
    except AttributeError as e:
        vec = data
        vec['vec_error'] = str(e)

    response = method(variables.API_URL + function, data=vec, timeout=timeout)
    if variables.IS_SERVICE_PROCESS:
        internet.check.setConnected()
    reason = data.get('reason', '?')
    json = response.json()
    try:
        if json.get('signed'):
            variables.WINDOW_HOME.setProperty('Vavoo_Signed', json['signed'])
            variables.addon.setSetting('signed', json['signed'])
        if json.get('data', {}).get('signed'):
            variables.WINDOW_HOME.setProperty('Vavoo_Signed', json['data']['signed'])
            variables.addon.setSetting('signed', json['data']['signed'])
    except Exception as e:
        xbmc.log('Failed getting signed: %s' % e, xbmc.LOGERROR)

    if 'error' in json:
        raise APIError(json)
    return json.get('response', None)


def guest(reason, timeout=None):
    data = {'reason': reason}
    json = _call(requests.post, 'box/guest', data)
    if not json:
        raise ValueError('Got no token')
    return json.get('token', None)


def checkEmail(email):
    data = {'email': email}
    json = _call(requests.post, 'box/signup/checkemail', data)
    if not json:
        raise ValueError('Got no ticket')
    return json['exists']


def signup(email, password, reason):
    data = {'email': email, 'password': password, 'reason': reason}
    json = _call(requests.post, 'box/signup', data)
    if not json:
        raise ValueError('Signup failed')
    if 'token' in json:
        return ('login', json['token'])
    return ('signup', json['ticket'])


def connectInit(token):
    data = {'token': token}
    json = _call(requests.post, 'box/connect/init', data)
    if not json:
        raise ValueError('Got no code')
    return json['code']


def connectCheck(token, code):
    data = {'token': token, 'code': code}
    json = _call(requests.post, 'box/connect/check', data)
    if not json:
        raise ValueError('Got no token')
    return (json['token'], json['email'])


def login(email, password, license=None):
    data = {'email': email, 'password': password}
    json = _call(requests.post, 'box/login', data)
    if not json:
        raise ValueError('Got no token')
    return json.get('token', None)


def logout(token):
    data = {'token': token}
    _call(requests.post, 'box/logout', data)


def passwordLost(email):
    data = {'email': email}
    json = _call(requests.post, 'user/lost', data)
    return json == 'success'


def ping(token, reason='none', infos=True, timeout=60, **data):
    if not token:
        return
    data.update({'token': token, 'reason': reason})
    return _call(requests.post, 'box/ping2', data, timeout=timeout)


def pay(token):
    data = {'token': token}
    json = _call(requests.post, 'box/pay', data)
    if not json:
        raise ValueError('Got no infos')
    return json.get('url', None)


def installText():
    return _call(requests.post, 'box/install/text', {})


def forceDevice(token):
    data = {'token': token}
    _call(requests.post, 'box/force', data)


def sendmailAdvertisement(token, reason):
    data = {'token': token, 'reason': reason}
    _call(requests.post, 'box/sendmail/advertisement', data)
# uncompyle6 version 3.7.4
# Python bytecode 2.7 (62211)
# Decompiled from: Python 2.7.17 (default, Sep 30 2020, 13:38:04) 
# [GCC 7.5.0]
# Embedded file name: /data/build/addons/service.vavoo/lib/install.py
# Compiled at: 2019-01-15 23:17:47
import xbmc, xbmcgui, requests
from lib import variables
from lib import vavoo_api
from lib import utils
from lib import internet
from lib import api
from lib import vprop
import os, hashlib, time, zipfile, shutil, threading

class TextThread(threading.Thread):
    cached = {}

    @classmethod
    def get(cls, name):
        try:
            return cls.cached[name]
        except Exception:
            return ''

    def __init__(self, window):
        super(TextThread, self).__init__()
        self.setDaemon(True)
        self.window = window
        self.setProperty()

    def setProperty(self):
        try:
            label = TextThread.get('label_' + xbmc.getLanguage(xbmc.ISO_639_1))
        except KeyError:
            label = TextThread.get('label')

        self.window.setProperty('WelcomeText', label)

    def run(self):
        try:
            TextThread.cached = api.installText()
            self.setProperty()
        except Exception as e:
            xbmc.log('Failed loading welcome text: %s' % e, xbmc.LOGERROR)


class WorkerThread(threading.Thread):

    def __init__(self, window, url):
        threading.Thread.__init__(self)
        self.window = window
        self.url = url
        self.p = 0

    def run(self):
        try:
            try:
                self._run()
            except ValueError as e:
                if e.message != 'CANCEL':
                    raise

        finally:
            self.window.clearProperty('ProgressWindow')
            self.window.setFocusId(self.window.URL_EDIT_ID)

    def _run(self):
        originalUrl = self.url
        while True:
            if not self.url.startswith('http'):
                self.url = 'http://' + self.url
            if not self.url.endswith('vavoo.json'):
                if not self.url.endswith('/'):
                    self.url += '/'
                self.url += 'vavoo.json'
            try:
                resp = requests.get(self.url)
                resp.raise_for_status()
                json = resp.json()
                self._updateProgress(add=3, max=10)
                redirect_url = json.get('redirect', None)
                if redirect_url:
                    xbmc.log('Redirecting bundle URL from %s to %s', self.url, redirect_url)
                    self.url = redirect_url
                    originalUrl = self.url
                    continue
                try:
                    json['url']
                    json['size']
                    json['sha1']
                except KeyError:
                    raise ValueError('Missing mandatory JSON keys')

            except Exception:
                utils.xbmcNotify(variables.localize(257), message=variables.localize(39527))
                raise
            else:
                break

        variables.addon.setSetting('install_url', originalUrl)
        zipPath = xbmc.translatePath('special://home/bundle.zip').decode('utf-8')
        tempPath = xbmc.translatePath('special://home/_bundle_temp').decode('utf-8')
        newPath = xbmc.translatePath('special://home/_bundle_new').decode('utf-8')
        self._updateProgress(set=10, text=variables.localize(39528))
        filecount = 0
        try:
            self._isLocalValid(zipPath, json)
        except ValueError:
            try:
                os.unlink(zipPath)
            except Exception:
                pass

            self._updateProgress(set=15, text=variables.localize(39529))
            resp = requests.get(json['url'], stream=True)
            time_started = time.time()
            last_status = 0
            bytes_processed = 0
            with open(zipPath, 'wb') as (f):
                for data in resp.iter_content(chunk_size=variables.BUFFER_SIZE):
                    filecount += 1
                    bytes_processed += len(data)
                    f.write(data)
                    t = time.time()
                    if t - last_status > 0.05:
                        last_status = t
                        p = 15 + float(bytes_processed) / (json['size'] or 1) * 45
                        speed = float(bytes_processed) / (t - time_started or 1)
                        self._updateProgress(set=p, text=variables.localize(39538) % (
                         float(bytes_processed) / json['size'] * 100,
                         utils.humansize(bytes_processed),
                         utils.humansize(json['size']),
                         utils.humansize(speed)))

            self._updateProgress(set=60, text=variables.localize(39530))
            self._isLocalValid(zipPath, json)

        if os.path.exists(tempPath):
            self._updateProgress(set=63, text=variables.localize(39530))
            shutil.rmtree(tempPath)
        self._updateProgress(set=70, text=variables.localize(39530))
        last_status = 0
        bytes_processed = 0
        with zipfile.ZipFile(zipPath, 'r') as (zip):
            for info in zip.infolist():
                zip.extract(info, tempPath)
                bytes_processed += info.compress_size
                t = time.time()
                if t - last_status > 0.05:
                    last_status = t
                    p = 70 + float(bytes_processed) / json['size'] * 20
                    self._updateProgress(set=p, text=variables.localize(39533) % (float(bytes_processed) / json['size'] * 100))

        self._updateProgress(set=90, text=variables.localize(39530))
        os.unlink(zipPath)
        if os.path.exists(newPath):
            self._updateProgress(set=92, text=variables.localize(39530))
            shutil.rmtree(newPath)
        self._updateProgress(set=95, text=variables.localize(39530))
        os.rename(tempPath, newPath)
        if filecount > 0:
            with open(os.path.join(newPath, 'valid'), 'w') as (f):
                f.write('valid')
        self._updateProgress(set=100, text=variables.localize(39599))
        installedPath = xbmc.translatePath('special://home/_bundle_installed').decode('utf-8')
        alreadyInstalled = os.path.exists(installedPath)
        if alreadyInstalled or json.get('reboot', True):
            time.sleep(2)
            vavoo_api.restart(rebootSystem=False)
        else:
            with open(installedPath, 'w') as (f):
                f.write('')
            self.window.close()
        return

    def _isLocalValid(self, path, json):
        if not os.path.exists(path):
            raise ValueError('Bundle not exists')
        if os.path.getsize(path) != json['size']:
            raise ValueError('Filesize is invalid')
        sha1 = hashlib.sha1()
        with open(path, 'rb') as (f):
            while True:
                data = f.read(variables.BUFFER_SIZE)
                if not data:
                    break
                sha1.update(data)

        sha1 = sha1.hexdigest()
        if sha1 != json['sha1']:
            raise ValueError('Checksum is invalid')

    def _updateProgress(self, set=None, add=None, max=100, text=None):
        self.window.setFocusId(self.window.WORK_CANCEL_BUTTON_ID)
        if self.window.cancel:
            raise ValueError('CANCEL')
        if set:
            self.p = set
        elif add:
            self.p = min(self.p + add, max)
        self.window.progress.setPercent(int(self.p))
        self.window.setProperty('ProgressLabel', text)


class InstallWindow(xbmcgui.WindowXML):
    URL_EDIT_ID = 100
    NEXT_BUTTON_ID = 300
    CANCEL_BUTTON_ID = 302
    INFO_BUTTON_ID = 303
    WORK_CANCEL_BUTTON_ID = 400
    WORK_PROGRESS_ID = 401

    @classmethod
    def create(cls):
        return cls('install.xml', variables.addonPath, 'Main', '1080i')

    def show(self):
        TextThread(self).start()
        self.alreadyInstalled = os.path.exists(xbmc.translatePath('special://home/_bundle_installed').decode('utf-8'))
        if self.alreadyInstalled:
            self.setProperty('BundleAlreadyInstalled', 'true')
        self.url = variables.addon.getSetting('install_url') or 'vavoo.tv'
        self.setProperty('Url', self.url)
        super(InstallWindow, self).show()

    def close(self):
        self.cancel = True
        utils.forceWindow.onClose()
        super(InstallWindow, self).close()

    def onInit(self):
        pass

    def askIfCancel(self):
        if xbmcgui.Dialog().yesno(variables.localize(39580), variables.localize(39581)):
            self.cancel = True

    def onAction(self, action):
        if self.alreadyInstalled:
            if action.getId() in (xbmcgui.ACTION_PREVIOUS_MENU, xbmcgui.ACTION_NAV_BACK):
                if self.getProperty('ProgressWindow') == 'true':
                    self.askIfCancel()
                    return
                self.close()
            else:
                utils.forceWindow.onAction(action)
            return super(InstallWindow, self).onAction(action)
        utils.forceWindow.onAction(action)

    def onClick(self, controlID):
        if controlID == self.URL_EDIT_ID:
            url = xbmcgui.Dialog().input(variables.localize(39539), self.url, xbmcgui.INPUT_ALPHANUM)
            if url:
                self.url = url
                self.setProperty('Url', self.url)
                self._check()
        elif controlID == self.NEXT_BUTTON_ID:
            self._check()
        elif controlID == self.CANCEL_BUTTON_ID:
            if self.alreadyInstalled:
                self.close()
            else:
                xbmc.executebuiltin('ActivateWindow(shutdownmenu)')
        elif controlID == self.INFO_BUTTON_ID:
            if TextThread.get('link') and hasattr(self, 'open_' + variables.getPlatformName()):
                getattr(self, 'open_' + variables.getPlatformName())()
        elif controlID == self.WORK_CANCEL_BUTTON_ID:
            self.askIfCancel()

    def open_vavoo(self):
        self.open_android()

    def open_android(self):
        xbmc.executebuiltin('StartAndroidActivity(,android.intent.action.VIEW,,' + TextThread.get('link') + ')')

    def open_linux(self):
        os.system("sensible-browser '" + TextThread.get('link') + "' &")

    def open_win32(self):
        os.system('explorer "' + TextThread.get('link') + '"')

    def open_osx(self):
        os.system("open '" + TextThread.get('link') + "'")

    def _check(self):
        url = self.url
        if not url:
            return
        internet.wait()
        self.setProperty('ProgressWindow', 'true')
        self.progress = self.getControl(self.WORK_PROGRESS_ID)
        self.cancel = False
        self.setFocusId(self.WORK_CANCEL_BUTTON_ID)
        WorkerThread(self, url).start()


def check():
    variables.assertNotServiceProcess()
    hasBundle = os.path.exists(xbmc.translatePath('special://home/_team.stube_').decode('utf-8'))
    if hasBundle:
        vprop.set('BundleInstalled', 'true')
    else:
        vprop.set('BundleInstalled', None)
        show()
    return


def show():
    variables.assertNotServiceProcess()
    if variables.WINDOW_HOME.getProperty('Locked') == 'true':
        return
    else:
        vprop.set('Locked', 'true')
        try:
            xbmc.executebuiltin('Dialog.Close(all,true)')
            utils.forceWindow.create(InstallWindow)
        finally:
            vprop.set('Locked', None)
            import login
            login.session.ping(reason='install')

        return
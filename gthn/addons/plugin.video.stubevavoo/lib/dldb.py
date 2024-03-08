import utils, xbmc, os, threading, json, xbmcgui, vjackson, time, urlparse, xbmcplugin, urllib2, requests, mimetypes, cgi
ENTRIES_TABLE = 'entries2'
SERVICE_CHANGE_TIMEOUT = 6
SERVICE_LOOP_INTERVAL = 3
CHUNK_SIZE = 16 * 1024

class Props(object):
    home = xbmcgui.Window(10000)

    @classmethod
    def get(cls, name):
        return cls.home.getProperty('DLDB_' + name)

    @classmethod
    def has(cls, name):
        return bool(cls.home.getProperty('DLDB_' + name))

    @classmethod
    def set(cls, name, value):
        return cls.home.setProperty('DLDB_' + name, value)

    @classmethod
    def clear(cls, name):
        return cls.home.clearProperty('DLDB_' + name)


wasActive = None

def isActive():
    global wasActive
    isActive = utils.addon.getSetting('dldb_active') == 'true'
    if isActive is not wasActive:
        wasActive = isActive
        if isActive:
            Props.set('Active', 'true')
        else:
            Props.clear('Active')
    return isActive


def getMaxSimultanDownloads():
    return int(utils.addon.getSetting('dldb_max_simultan_downloads'))


def getBasePath():
    basePath = utils.addon.getSetting('dldb_path')
    if not basePath:
        if xbmc.getCondVisibility('system.platform.android'):
            basePath = os.path.join('/sdcard', 'Download', 'VAVOO')
        else:
            if xbmc.getCondVisibility('system.platform.ios'):
                basePath = os.path.join(xbmc.translatePath('special://logpath'), 'VAVOO-Downloads')
            else:
                basePath = os.path.join(os.path.expanduser('~'), 'Downloads', 'VAVOO')
        utils.addon.setSetting('dldb_path', basePath)
    return basePath


def getDldbId(params):
    id = str(params['id'])
    if 'season' in params or 'episode' in params:
        id += 's%se%s' % (params['season'], params['episode'])
    id += params['language']
    return id


class Database(utils.Database):

    def __init__(self, basePath=None):
        if basePath is None:
            basePath = getBasePath()
        super(Database, self).__init__(basePath, 'VAVOO.db')
        self.init()
        return

    def init(self):
        c = self.cursor()
        try:
            try:
                c.execute('CREATE TABLE IF NOT EXISTS ' + ENTRIES_TABLE + ' (' + 'id VARCHAR(30) PRIMARY KEY,' + 'created INTEGER,' + 'modified INTEGER,' + 'type VARCHARR(20) NOT NULL,' + 'season INTEGER NOT NULL,' + 'episode INTEGER NOT NULL,' + 'language VARCHAR(2) NOT NULL,' + 'status VARCHAR(20),' + 'infos VARCHAR(1000),' + 'params TEXT,' + 'contents TEXT,' + 'data TEXT)')
                self.commit()
            except Exception:
                import traceback
                traceback.print_exc()

        finally:
            c.close()

    def insert(self, params, contents):
        id = getDldbId(params)
        data = {'id': id, 
           'type': contents['type'], 
           'season': contents['get'].get('season', 0), 
           'episode': contents['get'].get('episode', 0), 
           'language': params['language'], 
           'created': int(time.time()), 
           'modified': int(time.time()), 
           'status': 'pending', 
           'infos': '', 
           'params': json.dumps(params), 
           'contents': json.dumps(contents), 
           'data': json.dumps({})}
        c = self.cursor()
        try:
            try:
                c.execute('INSERT INTO %s (%s) VALUES (%s)' % (ENTRIES_TABLE, (',').join(data.keys()), (',').join(['?'] * len(data))), data.values())
                self.commit()
            except Exception:
                raise

        finally:
            c.close()

        Props.set(id, data['status'])
        entries = int(Props.get('Entries') or 0) + 1
        Props.set('Entries', str(entries))
        if entries == 1:
            xbmcgui.Dialog().ok('Download', 'Der Download wurde gestartet.', "Im Startmen\xc3\xbc befindet sich ein neuer Eintrag 'DOWNLOADS'. Du kannst Deine heruntergeladenen Dateien dar\xc3\xbcber einsehen & verwalten.")
        return entries

    def update(self, id, **kwargs):
        if 'status' in kwargs:
            if kwargs['status'] == 'error':
                xbmc.log('Setting %s to error with message %s' % (id, kwargs['infos']), xbmc.LOGERROR)
            else:
                kwargs['infos'] = ''
        kwargs['modified'] = int(time.time())
        keys = (', ').join([ key + '=?' for key in kwargs ])
        values = kwargs.values() + [id]
        c = self.cursor()
        try:
            c.execute('UPDATE %s SET %s WHERE id=?' % (ENTRIES_TABLE, keys), values)
            self.commit()
            print 'Database UPDATE %s / affected=%s / %s' % (id, c.rowcount, kwargs)
            if c.rowcount == 0:
                return
        finally:
            c.close()

        if 'status' in kwargs:
            Props.set(id, kwargs['status'])
            if kwargs['infos']:
                Props.set(id + '_Infos', kwargs['infos'])
            else:
                Props.clear(id + '_Infos')

    def delete(self, id):
        c = self.cursor()
        try:
            c.execute('DELETE FROM %s WHERE id=?' % ENTRIES_TABLE, [id])
            self.commit()
            print 'Database DELETE %s / affected=%s' % (id, c.rowcount)
            if c.rowcount == 0:
                return
        finally:
            c.close()

        Props.clear(id + '_Running')
        Props.clear(id + '_Cancel')
        Props.clear(id + '_Infos')
        Props.clear(id)
        Props.set('Entries', str(max(0, int(Props.get('Entries') or 0) - 1)))


class Worker(threading.Thread):
    running = 0

    def __init__(self, db, id):
        threading.Thread.__init__(self)
        self.setDaemon(True)
        self.basePath = db.basePath
        db = Database()
        try:
            c = db.cursor()
            try:
                c.execute('SELECT * FROM %s WHERE id=?' % ENTRIES_TABLE, [id])
                self.entry = c.fetchone()
            finally:
                c.close()

        finally:
            db.close()

        for key in self.entry.keys():
            setattr(self, key, self.entry[key])

        self.status = 'init'
        self.save('status')
        Props.clear(self.id + '_ForceStart')
        Worker.running += 1
        Props.set('Running', str(Worker.running))
        Props.set(self.id + '_Running', 'true')
        Props.clear(self.id + '_Cancel')
        print 'Download %s starting' % self.id
        self.start()

    def run(self):
        try:
            try:
                self._run()
                if self.status != 'complete' and not self.cancel():
                    raise RuntimeError('Download is not complete after thread end')
            except Exception as e:
                self.status = 'error'
                self.infos = e.message
                self.save('status', 'infos')
                import traceback
                traceback.print_exc()
                print 'Download %s ended with error %r' % (self.id, e)

        finally:
            if self.status in ('init', 'downloading'):
                self.status = 'pending'
                self.save('status')
            Worker.running -= 1
            Props.set('Running', str(Worker.running))
            Props.clear(self.id + '_Running')
            Props.clear(self.id + '_Cancel')
            print 'Download %s stopped with status %s' % (self.id, self.status)

    def _run(self):
        self.params = json.loads(self.params)
        self.contents = json.loads(self.contents)
        self.data = json.loads(self.data)
        if time.time() - self.modified > 1800:
            self.contents = vjackson.makeRequest('get', self.params, cache='short')
            self.save('contents')
        MyGet(self)

    def save(self, *args):
        update = {}
        for arg in args:
            update[arg] = getattr(self, arg)
            if isinstance(update[arg], dict):
                update[arg] = json.dumps(update[arg])

        db = Database(self.basePath)
        try:
            db.update(self.id, **update)
        finally:
            db.close()

    def cancel(self):
        if xbmc.abortRequested:
            return True
        if not isActive():
            return True
        if Props.has(self.id + '_Cancel'):
            return True
        if not Props.has(self.id + '_Running'):
            return True
        if self.basePath != getBasePath():
            return True
        return False


class MyGet(vjackson.get):

    def __init__(self, worker):
        self.worker = worker
        super(MyGet, self).__init__(worker.params)

    def init(self):
        if not self.worker.data.get('hash', None):
            import binascii
            crc32 = '%08x' % (binascii.crc32(self.worker.id) & 4294967295)
            self.hash = '%s%s' % (crc32, self.worker.id)
            self.worker.data['hash'] = self.hash
            self.worker.save('data')
        self.path = os.path.join(self.worker.basePath, self.worker.data['hash'])
        try:
            self.data = vjackson.makeRequest('get', self.params, cache=None)
        except Exception:
            import traceback
            traceback.print_exc()
            self.data = None
        else:
            self.worker.contents = self.data
            self.worker.save('contents')

        if not self.data:
            self.data = self.worker.contents
        return

    def allowMultiparts(self):
        return False

    def getStreamSelect(self):
        return 'auto'

    def checkCanceled(self):
        if self.worker.cancel():
            raise ValueError('CANCELED')

    def showFailedNotification(self):
        pass

    def initProgress(self):
        self.progress = None
        return

    def setMirrorProgress(self, *args, **kwargs):
        pass

    def findMirror(self):
        current = self.worker.data.get('current')
        if current:
            mirror = current.get('mirror')
            link = current.get('link')
            part = current.get('part')
            url = current.get('url')
            if not mirror or not link or not part or not url:
                xbmc.log('Failed continuing download cause incomplete of metadata', xbmc.LOGERROR)
            else:
                resolvedUrl = self.resolveUrl(mirror, link, url)
                if resolvedUrl:
                    if self.tryMirror(mirror, link, part, url, resolvedUrl):
                        return
        return super(MyGet, self).findMirror()

    def tryMirror(self, mirror, link, part, url, resolvedUrl):
        print 'Trying resolved URL: %s' % resolvedUrl
        try:
            if '|' not in resolvedUrl:
                resolvedUrl += '|'
            if '&User-Agent' not in resolvedUrl:
                resolvedUrl += '&User-Agent=' + urllib2.quote('Mozilla/5.0 (Windows; U; Windows NT 5.1; de-DE; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
            return self._tryMirror(mirror, link, part, url, resolvedUrl)
        except Exception as e:
            if isinstance(e, ValueError) and e.message == 'CANCELED':
                raise
            self.worker.status = 'init'
            self.worker.save('status')
            import traceback
            traceback.print_exc()
            import reporterror
            reporterror.report(utils.addonID, e, {'function': 'player', 'link': link, 'url': url})
            return False

    def _tryMirror(self, mirror, link, part, url, resolvedUrl):
        if int(part) != 1:
            raise RuntimeError('Part is not 1')
        if mirror['parts'] > 1:
            raise RuntimeError('Multipart not allowed')
        current = self.worker.data.get('current', {})
        basefile = os.path.join(self.path, '1')
        tempfile = basefile + '.downloading'
        startPos = 0
        if current.get('url') == url:
            if os.path.exists(tempfile):
                startPos = os.path.getsize(tempfile)
        if '|' in resolvedUrl:
            requestUrl, headers = resolvedUrl.split('|', 1)
            headers = urlparse.parse_qs(headers)
            headers = {key:value[0] if isinstance(value, (list, tuple)) else value for key, value in headers.items()}
        else:
            requestUrl = resolvedUrl
            headers = {}
        if startPos > 0:
            headers['Range'] = 'bytes=%s-' % startPos
        resp = requests.get(requestUrl, headers=headers, verify=False, stream=True)
        self.checkCanceled()
        totalSize = int(resp.headers['Content-Length']) + startPos
        contentType = resp.headers['Content-Type']
        ext = mimetypes.guess_extension(contentType)
        if ext == '.obj' or contentType.startswith('application/'):
            temp = cgi.parse_header(resp.headers['Content-Disposition'])
            try:
                filename = temp[1]['filename']
                contentType = mimetypes.guess_type(filename)[0]
                ext = mimetypes.guess_extension(contentType)
            except Exception as e:
                print 'Failed parsing Content-Disposition: %r %r %r' % (e, resp.headers, temp)

        if ext == '.obj' or contentType.startswith('application/'):
            contentType = mimetypes.guess_type(resp.url)[0]
            if contentType:
                ext = mimetypes.guess_extension(contentType)
        if ext == '.obj' or contentType.startswith('application/'):
            xbmc.log('Failed detecting file extension: %r %r' % (resp.url, resp.headers), xbmc.LOGWARNING)
            ext = '.unknown-format'
        Props.set(self.worker.id + '_Total', str(totalSize))
        if startPos > 0:
            unit, start = resp.headers['Content-Range'].split(' ', 1)
            if unit != 'bytes':
                raise RuntimeError('unit')
            start = int(start.split('-', 1)[0])
            if start != startPos:
                raise RuntimeError('startPos')
        if startPos == 0 and os.path.exists(tempfile):
            os.unlink(tempfile)
        self.checkCanceled()
        current = {'mirror': mirror, 
           'link': link, 
           'part': part, 
           'url': url}
        self.worker.data['current'] = current
        self.worker.data['fileext'] = ext
        self.worker.status = 'downloading'
        self.worker.save('data', 'status')
        try:
            try:
                if not os.path.exists(self.path):
                    os.makedirs(self.path)
                if not os.path.exists(tempfile):
                    with open(tempfile, 'wb'):
                        pass
                last = 0
                with open(tempfile, 'r+b') as (f):
                    if startPos > 0:
                        f.seek(startPos)
                    self.checkCanceled()
                    currentPos = startPos
                    speed = [(time.time(), currentPos)]
                    for chunk in resp.iter_content(chunk_size=CHUNK_SIZE):
                        f.write(chunk)
                        currentPos += len(chunk)
                        t = time.time()
                        speed.append((t, currentPos))
                        if t - last < 3:
                            continue
                        self.checkCanceled()
                        last = t
                        currentSpeed = float(currentPos - speed[0][1]) / (t - speed[0][0] or 1)
                        speed = speed[-30:]
                        eta = float(totalSize - currentPos) / currentSpeed
                        progress = float(currentPos) / totalSize * 100
                        print u'Download %s: pos=%s/%s speed=%s eta=%s progress=%s' % (self.worker.id, currentPos, totalSize, currentSpeed, int(eta), progress)
                        Props.set(self.worker.id + '_Pos', str(currentPos))
                        Props.set(self.worker.id + '_Speed', str(int(currentSpeed)))
                        Props.set(self.worker.id + '_ETA', str(int(eta)))
                        Props.set(self.worker.id + '_Progress', str(int(progress)))

                if currentPos != totalSize:
                    raise RuntimeError('Aborted during request')
                finalfile = basefile + ext
                if os.path.exists(finalfile):
                    try:
                        os.unlink(finalfile)
                    except Exception:
                        import traceback
                        traceback.print_exc()

                os.rename(tempfile, finalfile)
                self.worker.status = 'complete'
                self.worker.save('status')
                return True
            except Exception:
                raise

        finally:
            for key in ('Total', 'Pos', 'Speed', 'ETA', 'Progress'):
                Props.clear(self.worker.id + '_' + key)


def getExistingLanguages(params):
    existingLanguages = {}
    id = str(params['id'])
    if 'season' in params or 'episode' in params:
        id += 's%se%s' % (params['season'], params['episode'])
    try:
        language = params['language']
        if language == 'all':
            raise KeyError()
    except KeyError:
        id += 'XX'
        if 'languages' in params:
            languages = params['languages'].split(',')
        else:
            languages = ('de', 'en')
        for language in languages:
            id = id[:-2] + language
            status = Props.get(id)
            if status:
                existingLanguages[language] = (
                 id, status)
        else:
            status = ''

    id += language
    status = Props.get(id)
    if status:
        existingLanguages[language] = (
         id, status)
    return existingLanguages


def downloadAdd(params):
    progress = xbmcgui.DialogProgress()
    progress.create('VAVOO.TO', u'Der Download wird vorbereitet...')
    try:
        urlParams = vjackson.convertUrlParameter(params['url'])
        if not urlParams.get('language'):
            languages = urlParams.pop('languages').split(',')
            if len(languages) > 1:
                forceDialog = True
                existingLanguages = getExistingLanguages(urlParams)
                languages = list(set(languages) - set(existingLanguages.keys()))
                if not languages:
                    return
            else:
                forceDialog = False
            urlParams['languages'] = (',').join(languages)
            vjackson.getParamsLanguage(urlParams, forceDialog=forceDialog)
        progress.update(50)
        data = vjackson.makeRequest('get', urlParams, cache=None)
    finally:
        progress.close()

    try:
        db = Database()
        try:
            numEntries = db.insert(urlParams, data)
        finally:
            db.close()

    except Exception as e:
        import traceback
        traceback.print_exc()
        xbmcgui.Dialog().ok('Download', 'Fehler beim hinzuf\xc3\xbcgen des Downloads.', str(e.message))

    xbmc.executebuiltin('Dialog.Close(all,true)')
    xbmc.executebuiltin('Container.Refresh')
    if numEntries > 1:
        xbmcgui.Dialog().notification('Download', 'Der Eintrag wird in K\xc3\xbcrze heruntergeladen.', xbmcgui.NOTIFICATION_INFO)
    return


def handleUrlParamsAndLanguagesAndEntry(params):
    urlParams = vjackson.convertUrlParameter(params['url'])
    existingLanguages = getExistingLanguages(urlParams)
    if len(existingLanguages) > 1:
        temp = {'languages': (',').join(existingLanguages.keys())}
        vjackson.getParamsLanguage(temp)
        id = existingLanguages[temp['language']][0]
    else:
        id = existingLanguages.values()[0][0]
    db = Database()
    xbmc.executebuiltin('ActivateWindow(busydialog)')
    try:
        c = db.cursor()
        try:
            c.execute('SELECT * FROM %s WHERE id=?' % ENTRIES_TABLE, [id])
            entry = c.fetchone()
        finally:
            c.close()

    finally:
        db.close()

    return (
     urlParams, id, entry)


def downloadDelete(params):
    urlParams, id, entry = handleUrlParamsAndLanguagesAndEntry(params)
    xbmc.executebuiltin('ActivateWindow(busydialog)')
    try:
        data = json.loads(entry['data'])
        if Props.has(id + '_Running'):
            Props.set(id + '_Cancel', 'true')
            for _ in xrange(SERVICE_CHANGE_TIMEOUT):
                if not Props.has(id + '_Running'):
                    break
                xbmc.sleep(1000)

            if Props.has(id + '_Running'):
                xbmc.log('Could not stop download %s' % id, xbmc.LOGWARNING)
        db = Database()
        try:
            if data.get('hash'):
                path = os.path.join(db.basePath, data['hash'])
                basefile = os.path.join(path, '1')
                tempfile = basefile + '.downloading'
                if os.path.exists(tempfile):
                    try:
                        os.unlink(tempfile)
                    except Exception:
                        import traceback
                        traceback.print_exc()

                if 'fileext' in data:
                    finalfile = basefile + data['fileext']
                    if os.path.exists(finalfile):
                        try:
                            os.unlink(finalfile)
                        except Exception:
                            import traceback
                            traceback.print_exc()

                if os.path.exists(path):
                    try:
                        os.rmdir(path)
                    except Exception:
                        import traceback
                        traceback.print_exc()

            db.delete(entry['id'])
            xbmc.executebuiltin('Container.Refresh')
        finally:
            db.close()

    finally:
        xbmc.executebuiltin('Dialog.Close(all,true)')


def downloadForce(params):
    urlParams, id, entry = handleUrlParamsAndLanguagesAndEntry(params)
    if entry['status'] in ('pause', 'error'):
        db = Database()
        try:
            db.update(id, status='pending')
        finally:
            db.close()

    if not Props.has(id + '_Running'):
        Props.set(id + '_ForceStart', 'true')
        xbmc.executebuiltin('ActivateWindow(busydialog)')
        try:
            for _ in xrange(SERVICE_CHANGE_TIMEOUT):
                if Props.has(id + '_Running'):
                    break
                xbmc.sleep(1000)

        finally:
            xbmc.executebuiltin('Dialog.Close(all,true)')

    xbmc.executebuiltin('Dialog.Close(all,true)')
    xbmc.executebuiltin('Container.Refresh')


def downloadPauseToggle(params):
    urlParams, id, entry = handleUrlParamsAndLanguagesAndEntry(params)
    try:
        if entry['status'] in ('pending', 'error', 'init', 'downloading'):
            if Props.has(id + '_Running'):
                Props.set(id + '_Cancel', 'true')
                try:
                    for _ in xrange(SERVICE_CHANGE_TIMEOUT):
                        if not Props.has(id + '_Running'):
                            break
                        xbmc.sleep(1000)

                finally:
                    xbmc.executebuiltin('Dialog.Close(all,true)')

            if entry['status'] in ('pending', 'error', 'init', 'downloading'):
                db = Database()
                try:
                    db.update(id, status='pause')
                finally:
                    db.close()

        else:
            if entry['status'] == 'pause':
                db = Database()
                try:
                    db.update(id, status='pending')
                finally:
                    db.close()

    finally:
        xbmc.executebuiltin('Dialog.Close(all,true)')
        xbmc.executebuiltin('Container.Refresh')


def createListItemHook(urlParams, params, e, isPlayable, properties, contextMenuItems):
    if not isPlayable:
        return
    existingLanguages = getExistingLanguages(urlParams)
    downloadableLanguages = set(urlParams['languages'].split(',')) - set(existingLanguages.keys())
    if downloadableLanguages:
        properties['DLDB_Downloadable'] = 'true'
        contextMenuItems.append(('Download', 'RunScript(plugin.video.stubevavoo,action=download/add,url=?' + vjackson.convertPluginParams(urlParams) + ')'))
    if not existingLanguages:
        return
    language = existingLanguages.keys()[0]
    id, status = existingLanguages[language]
    if status:
        if not language:
            for language in ('de', 'en'):
                id = id[:-2]

        running = Props.get(id + '_Running')
        properties.update({'DLDB': id, 
           'DLDB_Status': status, 
           'DLDB_Infos': Props.get(id + '_Infos'), 
           'DLDB_Running': running, 
           'DLDB_Pos': Props.get(id + '_Pos'), 
           'DLDB_Total': Props.get(id + '_Total'), 
           'DLDB_Speed': Props.get(id + '_Speed'), 
           'DLDB_Eta': Props.get(id + '_ETA'), 
           'DLDB_Progress': Props.get(id + '_Progress')})
        url = vjackson.convertPluginParams(urlParams)
        if status in ('pending', 'error', 'init', 'downloading'):
            properties['DLDB_Pauseable'] = 'true'
            contextMenuItems.append(('Download pausieren', 'RunScript(plugin.video.stubevavoo,action=download/pausetoggle,url=?' + url + ')'))
        else:
            if status == 'pause':
                properties['DLDB_Resumeable'] = 'true'
                contextMenuItems.append(('Download fortsetzen', 'RunScript(plugin.video.stubevavoo,action=download/pausetoggle,url=?' + url + ')'))
        if status != 'complete' and not running and isActive():
            contextMenuItems.append(('Download erzwingen', 'RunScript(plugin.video.stubevavoo,action=download/force,url=?' + url + ')'))
        properties['DLDB_Deletable'] = 'true'
        contextMenuItems.append(('Download l\xc3\xb6schen', 'RunScript(plugin.video.stubevavoo,action=download/delete,url=?' + url + ')'))


def downloadList(params):
    xbmcplugin.setContent(utils.getPluginhandle(), 'movies')
    db = Database()
    try:
        try:
            c = db.cursor()
            try:
                where = [[], []]
                language = vjackson.getLanguage(params)
                if language != 'all':
                    where[0].append('language=?')
                    where[1].append(language)
                q = 'SELECT * FROM %s' % ENTRIES_TABLE
                if where[0]:
                    q += ' WHERE %s' % (' AND ').join(where[0])
                q += ' ORDER BY created DESC'
                c.execute(q, where[1])
                entries = c.fetchall()
            finally:
                c.close()

        except Exception:
            import traceback
            traceback.print_exc()
            raise

    finally:
        db.close()

    def callback(urlParams, params, e, isPlayable, properties, contextMenuItems):
        if isActive():
            contextMenuItems.append(('Alle Downloads anhalten', 'RunScript(plugin.video.stubevavoo,action=download/active,active=false)'))
        else:
            contextMenuItems.append(('Alle Downloads fortsetzen', 'RunScript(plugin.video.stubevavoo,action=download/active,active=true)'))

    for entry in entries:
        params = json.loads(entry['params'])
        e = json.loads(entry['contents'])
        params['action'] = 'get'
        o, media = vjackson.createListItem(params, params, e, addTypename=True, isPlayable=True, callback=callback)
        properties = {}
        properties['Languages'] = entry['language']
        if entry['type'] == 'serie':
            properties.update({'Sublabel': 'Season %s Episode %s' % (entry['season'], entry['episode']), 
               'selectaction': 'play_or_resume'})
        for key, value in properties.items():
            if not isinstance(value, basestring):
                value = str(value)
            o.setProperty(key, value)

        xbmcplugin.addDirectoryItem(handle=utils.getPluginhandle(), url=vjackson.getPluginUrl(params), listitem=o, isFolder=False)

    vjackson.addDir2('Einstellungen', 'settings', 'settings')
    xbmcplugin.endOfDirectory(utils.getPluginhandle(), succeeded=True, cacheToDisc=False)


def downloadActive(params):
    if params['active'] not in ('true', 'false'):
        raise ValueError('Invalid value')
    xbmc.executebuiltin('ActivateWindow(busydialog)')
    try:
        utils.addon.setSetting('dldb_active', params['active'])
        if params['active'] == 'false':
            for _ in xrange(SERVICE_CHANGE_TIMEOUT):
                if int(Props.get('Running')) <= 0:
                    break
                xbmc.sleep(1000)

        else:
            for _ in xrange(SERVICE_CHANGE_TIMEOUT):
                if int(Props.get('Entries') or 0) <= 0:
                    break
                if int(Props.get('Running') or 0) > 0:
                    break
                xbmc.sleep(1000)

        xbmc.executebuiltin('Container.Refresh')
    finally:
        xbmc.executebuiltin('Dialog.Close(all,true)')


def downloadGet(params):
    id = getDldbId(params)
    db = Database()
    try:
        c = db.cursor()
        try:
            c.execute('SELECT * FROM %s WHERE id=?' % ENTRIES_TABLE, [id])
            entry = c.fetchone()
        finally:
            c.close()

        if entry is None:
            return False
        params = json.loads(entry['params'])
        e = json.loads(entry['contents'])
        data = json.loads(entry['data'])
        info = ''
        localPlay = True
        if entry['status'] != 'complete':
            info = 'Der Download ist noch nicht abgeschlossen.'
            localPlay = False
        if entry['status'] == 'pause':
            pass
        if localPlay:
            path = os.path.join(db.basePath, data['hash'])
            basefile = os.path.join(path, '1')
            finalfile = basefile + data['fileext']
            if not os.path.exists(finalfile):
                xbmc.log('Complete file does not exists anymore: %s' % finalfile, xbmc.LOGWARNING)
                localPlay = False
                result = xbmcgui.Dialog().yesno('VAVOO.TO', 'Die heruntergeladene Datei existiert nicht mehr.', 'Dr\xc3\xbccke "Ja" um die Datei erneut herunterzuladen oder "Nein" um diesen Eintrag zu entfernen.')
                if result:
                    db.update(entry['id'], status='pending')
                    xbmc.executebuiltin('Container.Refresh')
                    info = 'Die Datei wird erneut heruntergeladen.'
                else:
                    db.delete(entry['id'])
                    xbmc.executebuiltin('Container.Refresh')
                    info = 'Der Eintrag wurde aus der Bibliothek entfernt.'
    finally:
        db.close()

    if not localPlay:
        result = xbmcgui.Dialog().yesno('VAVOO.TO', 'Eine Wiedergabe der heruntergeladenen Datei ist derzeit nicht m\xc3\xb6glich.', info, 'M\xc3\xb6chtest Du die Datei statt dessen Streamen?')
        if result:
            return False
        return True
    else:
        addTypename = True if type == 'all' else False
        o, media = vjackson.createListItem(params, params, e, addTypename, isPlayable=True)
        o.setPath(finalfile)
        xbmcplugin.setResolvedUrl(utils.getPluginhandle(), True, o)
        return True


def setServiceTerminated(infos):
    db = Database()
    try:
        try:
            c = db.cursor()
            try:
                c.execute("SELECT id FROM %s WHERE status NOT IN ('pending', 'complete')" % ENTRIES_TABLE)
                entries = c.fetchall()
            finally:
                c.close()

            for entry in entries:
                db.update(entry['id'], status='error', infos=infos)

        except Exception:
            import traceback
            traceback.print_exc()

    finally:
        db.close()


def service():
    time.sleep(10)


def service2():
    print 'DLDB service started'
    monitor = xbmc.Monitor()
    if monitor.waitForAbort(1):
        return
    db = Database()
    try:
        try:
            c = db.cursor()
            try:
                c.execute('SELECT id, status FROM %s' % ENTRIES_TABLE)
                entries = c.fetchall()
            finally:
                c.close()

        except Exception:
            import traceback
            traceback.print_exc()
            raise

    finally:
        db.close()

    for entry in entries:
        if entry['status'] not in ('pending', 'pause', 'complete'):
            print 'WARNING: Setting status of %s from %s to pending' % (entry['id'], entry['status'])
            db.update(entry['id'], status='pending')
        else:
            Props.set(entry['id'], entry['status'])

    Props.set('Entries', str(len(entries)))
    if monitor.waitForAbort(4):
        return
    try:
        try:
            waitForAbort = False
            while not monitor.abortRequested():
                n = getMaxSimultanDownloads() - Worker.running
                print 'Looping: isActive=%s, running=%s, space=%s' % (isActive(), Worker.running, n)
                if isActive():
                    db = Database()
                    try:
                        try:
                            c = db.cursor()
                            try:
                                t = time.time()
                                c.execute("UPDATE %s SET status='pending', infos='', modified=? WHERE status='error' AND modified<?" % ENTRIES_TABLE, [
                                 int(t), int(t - 600)])
                                c.execute("SELECT id, status FROM %s WHERE status='pending' ORDER BY created ASC" % ENTRIES_TABLE)
                                entries = c.fetchall()
                            finally:
                                c.close()

                        except Exception:
                            import traceback
                            traceback.print_exc()

                    finally:
                        db.close()

                    for entry in entries:
                        if Props.has(entry['id'] + '_Running'):
                            continue
                        if not Props.has(entry['id'] + '_ForceStart'):
                            continue
                        print 'Starting download %r' % entry['id']
                        Worker(db, entry['id'])
                        n -= 1

                    for entry in entries:
                        if Props.has(entry['id'] + '_Running'):
                            continue
                        if n <= 0:
                            break
                        print 'Starting download %r' % entry['id']
                        Worker(db, entry['id'])
                        n -= 1

                if monitor.waitForAbort(SERVICE_LOOP_INTERVAL):
                    waitForAbort = True
                    break

        except Exception as e:
            import traceback
            traceback.print_exc()
            setServiceTerminated('Service terminated: %s' % e.message)
            raise
        else:
            setServiceTerminated('Service terminated')
            print 'DLDB service stopped with abortRequested=%s, waitForAbort=%s' % (monitor.abortRequested(), waitForAbort)

    finally:
        print 'DLDB service stopped'
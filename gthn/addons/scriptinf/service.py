#!/usr/bin/python
# -*- coding: utf-8 -*-

import xbmc
import os
import urllib
import xbmcgui

try:
    home_path = xbmc.translatePath('special://home/addons/version').decode('utf-8')
    try:
        with open(home_path, 'r') as g:
            versionhome = g.read()
    except:
        versionhome = '0'
    url = 'https://ngpeqq.db.files.1drv.com/y4m84knvUfYbB-Pt73Cy2pnE79wM3aOmSA5ZaF1dSMzv32-Xzx2M0sa5HlY90aUEm11P38ylcFfhasQmt_5CJod6njcH9kEoiTmrp8NALI5sXhcWF-OruS_-wdPzjkpLQV166pDNifdt5Fs5BgWNnw5iXMk3Pa5E1eyOCgjrTz5NGoPBLSEcGH0JRY7DuqIqf-96Aho20DYLQrBpP3nSichbw'
    url1 = urllib.urlopen(url)
    versionurl = url1.read()

    if versionhome < versionurl:
        dialog = xbmcgui.Dialog()
        dialog.ok('STUBE.BOX.PRO DAS SYSTEM AKTUALİSİEREN','Ein neues Update ist verfügbar. Gehen Sie zu den Einstellungen und aktualisieren Sie es!')
except:
    pass
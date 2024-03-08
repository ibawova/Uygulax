import xbmcgui

INPUTSTREAM_PROTOCOLS = {
    'mpd': 'inputstream.adaptive',
    'ism': 'inputstream.adaptive',
    'hls': 'inputstream.adaptive',
    'rtmp': 'inputstream.rtmp'
}

class Helper:
    def __init__(self, protocol, drm=None):
        self.protocol = str(protocol).lower().strip()
        self.drm = str(drm or '').lower().strip()
        self.inputstream_addon = INPUTSTREAM_PROTOCOLS[protocol]

    def check_inputstream(self):
        xbmcgui.Dialog().ok('[MOVED]', 'Inputstream Helper addon has moved into the "SlyGuy InputStream Helper Wrapper Repository". That can be installed from the main SlyGuy Repository')

# -*- coding: utf-8 -*-
import xbmcgui, xbmcplugin, urllib2

addon_handle = int(sys.argv[1])
xbmcplugin.setContent(addon_handle, "movies")
network = True
try:
	url = urllib2.urlopen("http://tools.indecentes-voisines.com/flash.php?cat=all&sort=new&qte=1000")
except:
	network = False
if network == True:	
	s = list(url.read()[8:])
	url.close()
	posAnf = len(s)-2
	s[posAnf] = ';'
	title = "".join(s).replace("(vidE38o exclusive)", "").replace(" ! ", "").replace(" !", "").replace("E43", "&").replace("E42", "a").replace("E41", "e").replace("E40", "a").replace("E39", "e").replace("E38", "e").replace('&quot;', '"').replace("\\xab\\xa0", "<< ").replace("\\xa0\\xbb", " >>").replace("\\\\\\", "").replace("\\x92", "'").replace("\\x85", "...").replace("\\", "")
	endeID = title.find("::") 
	anfangBSFind = title.find("::", endeID+1)
	anfangBS = anfangBSFind + 2
	endeBS = title.find(";;", anfangBS)
	id = title[:endeID]
	startID = id
	desc = title[anfangBS:endeBS]
	if len(desc) > 1:
		stream = "http://flv.indecentes-voisines.com/extraits/"+id+".mp4"
		thumb = "http://img.indecentes-voisines.com/thumbs/cache/160x120_"+id+"_6.jpg"
		xbmcplugin.addDirectoryItem(handle=addon_handle, url=stream, listitem=xbmcgui.ListItem(desc, iconImage=thumb))
	while True:
		endeBSAlt = endeBS
		endeID = title.find("::", endeBS +1)
		anfangBSFind = title.find("::", endeID+1)
		anfangBS = anfangBSFind + 2
		endeBS = title.find(";;", anfangBS)
		if startID == title[endeBSAlt+2:endeID]:
			break
		if not (anfangBS == endeBS):
			id = title[endeBSAlt+2:endeID]
			desc = title[anfangBS:endeBS]
			stream = "http://flv.indecentes-voisines.com/extraits/"+id+".mp4"
			thumb = "http://img.indecentes-voisines.com/thumbs/cache/160x120_"+id+"_6.jpg"
			xbmcplugin.addDirectoryItem(handle=addon_handle, url=stream, listitem=xbmcgui.ListItem(desc, iconImage=thumb))
	xbmcplugin.endOfDirectory(addon_handle)
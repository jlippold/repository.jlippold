import sys
import urllib
import urllib2
import urlparse
import xbmcgui
import xbmcplugin
import xbmcaddon
import json
import time
import uuid
import re

from ring_doorbell import Ring
from datetime import datetime
from dateutil import tz


base_url = sys.argv[0]
addon_handle = int(sys.argv[1])
args = urlparse.parse_qs(sys.argv[2][1:])

xbmcplugin.setContent(addon_handle, 'movies')

mode = args.get('mode', None)

def init():

    ADDON = xbmcaddon.Addon(id='plugin.video.ring_doorbell')
    email = ADDON.getSetting('email')
    password = ADDON.getSetting('password')
    items = ADDON.getSetting('items')

    if len(email) <= 7: 
        return showModal('Invalid email address, check addon settings')
    if not re.match(r'[\w.-]+@[\w.-]+.\w+', email):
        return showModal('Invalid email address, check addon settings')
    if len(password) <= 3:
        return showModal('Invalid ring password, check addon settings')
    if items.isdigit() == False:
        return showModal('Invalid item count, check addon settings')
    
    try:
        myring = Ring(email, password)
    except:
        return showModal('Authentication Error: Check your ring.com credentials')

    if mode is None:
        events = []
        for device in list(myring.stickup_cams + myring.doorbells):
            for event in device.history(limit=items):
                event['formatted'] = format_event(device, event)
                event['doorbell_id'] = device.id
                events.append(event)
        sorted_events = sorted(events, key=lambda k: k['id'], reverse=True) 
        for event in sorted_events:
            url = build_url({'mode': 'play', 'doorbell_id': event['doorbell_id'], 'video_id': event['id']})
            li = xbmcgui.ListItem(str(event['formatted']), iconImage='DefaultVideo.png')
            xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=True)
        xbmcplugin.endOfDirectory(addon_handle)
    else: 
        if mode[0] == 'play':
            doorbell_id = args['doorbell_id'][0]
            video_id = args['video_id'][0]
            for doorbell in list(myring.stickup_cams + myring.doorbells):
                if doorbell.id == doorbell_id:
                    try:
                        url = doorbell.recording_url(video_id)
                        play_video(url)
                    except:
                        return showModal('Error playing video, it is possible that the video was not found on Ring.com')

def play_video(path):
    if xbmc.Player().isPlaying():
        xbmc.Player().stop()

    play_item = xbmcgui.ListItem(path=path)
    xbmc.Player().play(item=path, listitem=play_item)

def build_url(query):
    return base_url + '?' + urllib.urlencode(query)

def build_url2(query):
    return base_url + ', ' + urllib.urlencode(query)

def format_event(device, event):
    from_zone = tz.tzutc()
    to_zone = tz.tzlocal()
    utc = event['created_at'].replace(tzinfo=from_zone)
    local = utc.astimezone(to_zone)
    formatted = local.strftime('%I:%M %p on %A %b %d %Y')
    if event['kind'] == 'on_demand':
        formatted = device.name + " Live View at %s" % formatted
    if event['kind'] == 'motion':
        formatted = device.name + " Motion at %s" % formatted
    if event['kind'] == 'ding':
        formatted = device.name + " Ring at %s" % formatted
    return formatted

def showModal(text):
    __addon__ = xbmcaddon.Addon()
    __addonname__ = __addon__.getAddonInfo('name')
    xbmcgui.Dialog().ok(__addonname__, text)

init()
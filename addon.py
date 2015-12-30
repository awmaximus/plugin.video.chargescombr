from xbmcswift2 import Plugin

import sys
import urllib
import urllib2
import json
import gzip
import StringIO

USER_AGENT = 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) Gecko/20100101 Firefox/40.1'
REFERER = 'http://player.mais.uol.com.br'

BASE_LIST_URL = 'http://mais.uol.com.br/sys/content/listResumed.json?types=V,S&codProfile=efu0mq20a6k4&index.currentPage=1&index.itemsPerPage={0}'
BASE_INFO_URL = 'http://mais.uol.com.br/apiuol/v3/player/getMedia/{0}.json'
BASE_THUMB_URL = 'http://thumb.mais.uol.com.br/{0}.jpg'
POS_STREAM_URL = '|Referer={0}&User-Agent={1}'.format(REFERER,USER_AGENT)

RESOLUTION_CODE_MAP = {'360p':'2','720p':'5','1080p':'7'}

plugin = Plugin()

def GetJSON(url,is_gzip):
  request = urllib2.Request(url)
  if is_gzip: request.add_header('Accept-encoding', 'gzip')
  response = urllib2.urlopen(request)
  jsonstr = ''
  if is_gzip:
    buf = StringIO.StringIO(response.read())
    f = gzip.GzipFile(fileobj=buf)
    jsonstr = f.read()
    jsonDict = json.loads(jsonstr)
  else:
    jsonstr = response.read()
    jsonDict = json.loads(jsonstr)
  #print jsonstr
  return jsonDict

def GetVideoURL(id):
  resolution = plugin.get_setting('chargescombr.resolution',str)
  resolution_code_config = RESOLUTION_CODE_MAP[resolution]
  resolution_code_default = RESOLUTION_CODE_MAP['360p']
  info = GetJSON(BASE_INFO_URL.format(id),False)
  videoformats = info['item']['formats']
  urls = {}
  for videoformat in videoformats:
    urls[str(videoformat['id'])] = videoformat['url']+POS_STREAM_URL
  if urls.has_key(resolution_code_config):
    return urls[resolution_code_config]
  return urls[resolution_code_default]

@plugin.route('/')
def index():
  items = []
  limit = plugin.get_setting('chargescombr.limit',str)
  videos = GetJSON(BASE_LIST_URL.format(limit),False)
  for video in videos['contentsFromAuthorPage']:
    id = video['idtMedia']
    subject = video['namSubject']
    img = BASE_THUMB_URL.format(id)
    videourl = GetVideoURL(id)
    items.append({'label': subject, 'icon': img, 'path': videourl, 'is_playable': True})
  return items

if __name__ == '__main__':
    plugin.run()

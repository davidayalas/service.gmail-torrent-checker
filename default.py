import xbmcaddon
import xbmc
import imaplib
import httplib
import base64
import sys
import time
from json import dumps

settings = xbmcaddon.Addon(id='service.gmail-torrent-checker')

#################################################
#	SETUP
#################################################
host = settings.getSetting("imap_host") if settings.getSetting("imap_host") is not "" else "imap.gmail.com"
port = settings.getSetting("imap_port") if settings.getSetting("imap_port") is not "" else 993
user = settings.getSetting("imap_username")
pwd = settings.getSetting("imap_password")

transmission_host = settings.getSetting("transmission_host") if settings.getSetting("transmission_host") is not "" else "localhost"
transmission_port = settings.getSetting("transmission_port") if settings.getSetting("transmission_port") is not "" else "9091"
transmission_user = settings.getSetting("transmission_username")
transmission_pwd = settings.getSetting("transmission_password")

crontime = settings.getSetting("cron")
avoid_strs = settings.getSetting("avoid_strings")
search_subject = settings.getSetting("search_subject") if settings.getSetting("search_subject") is not "" else "torrent email"
################################################
 
try:
	crontime = float(crontime)
except exceptions.ValueError:
	crontime = 900

try:
	port = int(port)
except exceptions.ValueError:
	port = 993

if avoid_strs is not None and avoid_strs is not "":
	avoid_strs = avoid_strs.split(",")
else:
	avoid_strs = []

transmission_auth=""
if transmission_user is not "":
	transmission_auth = base64.encodestring('%s:%s' % (transmission_user, transmission_pwd)).replace('\n', '')

retry_timeout = 60

def addTorrent(torrent):
	""" Adds a torrent in the host
		param @torrent is String (http://uri-to-torrent or magnet:?)

		return Boolean
	"""

	path = "/transmission/rpc"

	try:
		conn = httplib.HTTPConnection(transmission_host + ":" + transmission_port)
		headers = {"Authorization": "Basic %s" % transmission_auth}
		conn.request("POST", "/transmission/rpc","",headers)
		response = conn.getresponse()
		sessionId = response.getheader('x-transmission-session-id')
		body = dumps({
						"method": "torrent-add",
	                	"arguments": { 
	                		"filename": torrent 
	                	} 
	                })
		headers = {
			"Authorization": "Basic %s" % transmission_auth,
			"Content-type": "application/x-www-form-urlencoded",
			"Accept": "text/plain",
			"x-transmission-session-id":sessionId
		}
		conn.request("POST", path, body, headers)
		return True
		
	except:
		e = sys.exc_info()[0]
		print "Torrent injection error: " + str(e)
		return False


def showMessage(header,message):
	xbmc.executebuiltin('Notification("'+header+'","'+message+'",5000)')

def main():
	""" Main functionallity that checks for new emails
	
	"""

	print "checking torrents"

	mail = None

	try:
		mail = imaplib.IMAP4_SSL(host, port)
	except:
		print "IMAP connection error. Retrying in "+str(retry_timeout)+" seconds"

	try:
		mail.login(user, pwd)
	except:
		mail = None
		print "Login error"

	if mail is not None:

		mail.select("inbox")

		result, data = mail.search(None, '(UNSEEN HEADER Subject "'+search_subject+'")') #search for unread emails with the subject provided in settings

		ids = data[0]
		uids = ids.split()

		if len(ids) is 0:
			print "No new torrents"

		for uid in uids:
			result, data = mail.fetch(uid, "(BODY.PEEK[])")
			message = data[0][1]
			message = message[message.find("Content-Type: text/plain;"):]
			message = message[message.find("\r"):]
			message = message[:message.find("Content-Type")]
			lines = message.split("\n\r")
			last = ""

			for l in lines:
				l = l.replace("\r","").replace("\n","")
				ll = l.lower()
				if (l.find("magnet:?")==0 or l.find("http://")==0 or l.find("https://")==0): 
					if len(avoid_strs) is 0 or (not any((s in last) for s in avoid_strs) and not any((s in ll) for s in avoid_strs)):	
						if addTorrent(l) == True: #if torrent has been added, then marks as read the email
							mail.store(uid, '+FLAGS', '\Seen')	
							print "torrent added: " + l
							showMessage("torrent added", l)
						else:
							print "error injecting torrent: " + l
							showMessage("error injecting torrent", l)

						break

					else:
						print "torrent discarded because of excluded strings: " + l

				if len(l)>0:
					last = l.lower()

		mail.expunge()		
		mail.close()
		mail.logout()
		time.sleep(crontime)
		main() 
	else:
		print retry_timeout
		time.sleep(retry_timeout)
		main()
		

#if user is setted then starts the process
if user is not "" and user is not None:
	main()
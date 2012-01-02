import mailbox
import re
import yaml
import time
import twitter

config = yaml.load(file("../config.yaml"))
api = None

def combineLines(lines):
	res = []
	cur = ""

	for line in lines:
		line = re.sub(r'^>+ *', "", line)
		if not len(line.strip()):
			if len(cur):
				res.append(cur)
				cur = ""
		else:
			if not len(cur):
				cur = line
			else:
				cur = cur + " " + line

	return res


def getApi():
        global api, config

        if api: 
                return api

        tw = config["twitter"]

        # See https://dev.twitter.com/docs/auth/tokens-devtwittercom
        # to understand how to get these

        api = twitter.Api(tw["consumer_key"], tw["consumer_secret"], tw["access_token"], tw["access_token_secret"])

        return api


mconfig = config["mail"]

mb = mailbox.UnixMailbox(file(mconfig["file"], "r"))

lastCheck = 0
lastCheckFile = None

try:
	lastCheckFile = file(mconfig["lastCheckFile"], "r")
	lastCheck = int(lastCheckFile.read())
except:
	print "no last check"
	pass
finally:
	if lastCheckFile:
		lastCheckFile.close()

# loop through mailbox to find emails responding to possible tweets

msg = mb.next()

while msg is not None:
	fromMatches = re.search(mconfig["client"], msg.unixfrom)
	subjectMatches = re.search(mconfig["subject"], msg["subject"])

	if fromMatches and subjectMatches:
		t = time.strptime(msg["date"], "%a, %d %b %Y %H:%M:%S -0500")

		msgTime = int(time.mktime(t))

#		print msg["subject"], "lastCheck", lastCheck, "msgTime", msgTime

		if msgTime > lastCheck:
			body = msg.fp.read()
			lines = combineLines(body.splitlines())
			for line in lines:
#				api = tweet.getApi()
#				api.PostUpdate(line)
				print "tweet:", line

		lastCheckFile = open(mconfig["lastCheckFile"], "w")
		lastCheckFile.write(str(int(time.mktime(t))))
		lastCheckFile.close()

	msg = mb.next()


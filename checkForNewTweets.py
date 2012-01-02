import urllib2
import simplejson
import os
import random
import re
import unicodedata
import smtplib
import yaml
import time

from email.mime.text import MIMEText

CACHE_LASTID = './cache/lastId'
CACHE_TWEETS = './cache/tweets'

TWEETS_PER_PAGE = 200

MIN_HALF = 10

SPLIT_WORDS = ["as", "of", "on", "in", "if", "at", "to", "and"]

config = yaml.load(file("config.yaml"))
mconfig = config["mail"]
tw = config["twitter"]

def unicode2ascii(text):
    if type(text) == unicode:
        return unicodedata.normalize("NFKD", text).encode("ascii", "ignore")
    else:
        return text

def sendMail(mfrom, to, body):
	msg = MIMEText(body)

	msg["Subject"] = "mailandglobe"
	msg["From"] = mfrom
	msg["To"] = to

	s = smtplib.SMTP('localhost')
	s.sendmail(mfrom, [to], msg.as_string())
	s.quit()

def getNewTweets(screenName, numberOfTweets):
    lastId = -1
    res = []

    if os.path.exists(CACHE_LASTID):
        f = open(CACHE_LASTID, 'r')
        lastId = f.readline()
        f.close()

    # Add "Since ID" to URL if we've cached up to the particular ID

    page = 0

    pages = numberOfTweets / TWEETS_PER_PAGE
    tweetsRem = numberOfTweets

    while page < pages: # max number of pages (of 200 tweets per page)
        nTweets = min(TWEETS_PER_PAGE, tweetsRem)
        url = 'https://api.twitter.com/1/statuses/user_timeline.json?include_entities=true&include_rts=true&screen_name={0}&count={1}&page={2}'.format(screenName, nTweets, page)

        if lastId >= 0:
            url += "&since_id=" + lastId

        attempts = 0

        while attempts < 5:
            try:
                print "Fetching page", page, url
                response = urllib2.urlopen(url).read()
                json_response = simplejson.loads(response)
                res += json_response
                break
            except:
                print "Failed, retrying in", 1 << atempts, "seconds"
                time.sleep(1 << attempts)
                attempts = attempts + 1

        # If there are less than nTweets responses,
        # then that's probably all of the tweets

        if len(json_response) < nTweets:
            break

        tweetsRem = tweetsRem - TWEETS_PER_PAGE
        page += 1

    return res

def getCachedTweets():
    # print "Get cached tweets"

    if os.path.exists(CACHE_TWEETS):
        f = open(CACHE_TWEETS, 'r')
        res = simplejson.loads(f.read())
        f.close()
        return res
    else:
        return []

def storeTweets(tweets, lastId):
    # print "Storing tweets"

    if not os.path.exists('./cache/'):
        os.mkdir('./cache/')

    f = open(CACHE_TWEETS, 'w')
    f.write(simplejson.dumps(tweets))
    f.close()

    f = open(CACHE_LASTID, 'w')
    f.write(str(lastId))
    f.close()

def prettify(tweet):
    text = tweet['text']

    # ignore retweets
    if "RT" in text: return None

    # ignore video 
    if "Video:" in text: return None

    # ignore live
    if "LIVE" in text: return None

    # remove bit.ly, tgam.ca, @s
    split = text.split(" ")

    unsplit = []

    for s in split:
        if "bit.ly" not in s and "tgam.ca" not in s and "@" not in s and "#" not in s and "http" not in s and "..." not in s:
            unsplit.append(s)

    ftext = ' '.join(unsplit)

    if ftext[-1] == ":":
        ftext = ftext[:-1]

    return ftext
    

newTweets = getNewTweets(tw["scrape_screen_name"], tw["number_of_tweets"])
cachedTweets = getCachedTweets()

print "New tweets: %d" % len(newTweets)

lastId = -1
for tweet in newTweets + cachedTweets:
    lastId = max(lastId, tweet["id"])

storeTweets(newTweets + cachedTweets, lastId)

# create dictionaries of before and after

splitDict = {}

for word in SPLIT_WORDS:
    splitDict[word] = [[], []]

    for tweet in cachedTweets:
        line = prettify(tweet)

        if not line:
            continue

        split = line.split(" " + word + " ")

        if len(split) >= 2:
            secondhalf = (" " + word + " ").join(split[1:])
            if len(split[0]) > MIN_HALF: splitDict[word][0].append(split[0])
            if len(secondhalf) > MIN_HALF: splitDict[word][1].append(secondhalf)

msg = ""

for tweet in newTweets:
    line = prettify(tweet)

    if not line:
       continue

    choices = []

    for word in SPLIT_WORDS:
        if " " + word + " " not in line:
            continue

        max0 = len(splitDict[word][0])-1
        max1 = len(splitDict[word][1])-1
        if max0 <= 0 and max1 <= 0: continue

        linesplit = line.split(" " + word + " ")
        linefirsthalf = linesplit[0]
        linesecondhalf = (" " + word + " ").join(linesplit[1:])

        if len(linefirsthalf) > MIN_HALF:
            for i in range(10):
                j = random.randint(0, max1)
                secondhalf = splitDict[word][1][j]
                choices.append(linefirsthalf + " " + word + " " + secondhalf)

        if len(linesecondhalf) > MIN_HALF:
            for i in range(10):
                j = random.randint(0, max0)
                firsthalf = splitDict[word][0][j]
                choices.append(firsthalf + " " + word + " " + linesecondhalf)

    # so it turns out if we put some random stuff at the end it could also be funny

    for word in SPLIT_WORDS:
        max1 = len(splitDict[word][1])-1
        if max1 <= 0: continue

        for i in range(5):
            j = random.randint(0, max1)
            secondhalf = splitDict[word][1][j]
            choices.append(line + " " + word + " " + secondhalf)

    # remove duplicates

    choices = list(set(choices))

    # remove any over 140 chars

    choices = filter(lambda x : len(x) <= 140, choices)

    # replace apostrophe

    choices = map(lambda x : unicode2ascii(x), choices)

    # replace all double spaces

    choices = map(lambda x : re.sub(r' +', ' ', x), choices)

    # okay now write 20 of these randomly
    
    random.shuffle(choices)
    choices = choices[0:min(20, len(choices)-1)]
    choices.sort()

    msg += "- " + unicode2ascii(line) + "\n"

    for choice in choices:
        msg += choice + "\n"

    msg += "\n"

if len(msg):
	sendMail(mconfig["server"], mconfig["client"], msg)

import urllib2
import simplejson
import os
import random
import re
import unicodedata
import smtplib
import yaml

CACHE_LASTID = './cache/lastId'
CACHE_TWEETS = './cache/tweets'
TWITTER_SCREEN_NAME = 'globeandmail'
TWEETS = 200
#PAGES = 16
PAGES = 1
MIN_HALF = 10

SPLIT_WORDS = ["as", "of", "on", "in", "if", "at", "to"]

config = yaml.load(file("config.yaml"))
mconfig = config["mail"]

def unicode2ascii(text):
    if type(text) == unicode:
        return unicodedata.normalize("NFKD", text).encode("ascii", "ignore")
    else:
        return text

def sendMail(mfrom, to, msg):
	s = smtplib.SMTP('localhost')
	s.sendmail(mfrom, [to], msg)
	s.quit()

def getNewTweets():
    lastId = -1
    res = []

    if os.path.exists(CACHE_LASTID):
        f = open(CACHE_LASTID, 'r')
        lastId = f.readline()
        f.close()

    # Add "Since ID" to URL if we've cached up to the particular ID

    page = 0

    while page < PAGES: # max number of pages (of 200 tweets per page)
        url = 'https://api.twitter.com/1/statuses/user_timeline.json?include_entities=true&include_rts=true&screen_name={0}&count={1}&page={2}'.format(TWITTER_SCREEN_NAME, TWEETS, page)

        if lastId >= 0:
            url += "&since_id=" + lastId

        print "Fetching page", page, url
        response = urllib2.urlopen(url).read()
        json_response = simplejson.loads(response)
        res += json_response

        # If there are less than TWEETS responses, then check the next page

        if len(json_response) < TWEETS:
            break

        page += 1

    return res

def getCachedTweets():
    print "Get cached tweets"
    if os.path.exists(CACHE_TWEETS):
        f = open(CACHE_TWEETS, 'r')
        res = simplejson.loads(f.read())
        f.close()
        return res
    else:
        return []

def storeTweets(tweets, lastId):
    print "Storing tweets"

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
    

newTweets = getNewTweets()
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

    # replace all double spaces

    choices = map(lambda x : re.sub(r' +', ' ', x), choices)

    # remove any over 140 chars

    choices = filter(lambda x : len(x) <= 140, choices)

    # replace apostrophe

    choices = map(lambda x : unicode2ascii(x), choices)

    # okay now write 20 of these randomly
    
#    if not os.path.exists('./newtweets/'):
#        os.mkdir('./newtweets/')
#
#    f = open('./newtweets/' + str(tweet["id"]), 'w')

    random.shuffle(choices)
    choices = choices[0:min(20, len(choices)-1)]
    choices.sort()

    for choice in choices:
        msg += choice + "\n\n"

#    for choice in choices:
#        try:
#            f.write(choice)
#            f.write("\n\n")
#        except:
#            print choice
#            pass

#    for choice in choices:
#        try:
#            f.write(choice + "\n")
#        except:
#            x = 1

#    f.close()

print msg
sendMail(mconfig["server"], mconfig["client"], msg)

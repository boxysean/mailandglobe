# The Mail and Globe

## About

[@mailandglobe](http://www.twitter.com/mailandglobe) tweets frankenstein versions of [@globeandmail](http://www.twitter.com/globeandmail) tweets, called frankentweets.

### Definition

Given a database of N tweets, a *frankentweet* is

1. a tweet joined using a preposition from two half-tweets in the database broken apart by the same preposition; or
2. a full tweet from the database, followed by a preposition and a half-tweet from the database that begins with the same preposition.

### Examples

    Frankentweet: European stocks higher on $3.48-billion sale of missiles, technology to UAE
    Tweet_1: European stocks higher on first trading day of 2012: tgam.ca/DN9s (Jan 2, 2012)
    Tweet_2: US seals deal on $3.48-billion sale of missiles, technology to UAE: http://tgam.ca/DNYo (Dec 31, 2011)

    Frankentweet: Patriots' Brady becomes third QB in Surrey RCMP custody
    Tweet_1: Patriots' Brady becomes third QB in NFL history with 5,000 yards in season: tgam.ca/DN4N (Jan 1, 2012)
    Tweet_2: Vancouver police to investigate death of man in Surrey RCMP custody: http://tgam.ca/DN19 (Dec 31, 2011)

    Frankentweet: Bobby Orr inspires Canada to win over U.S. at the parenting corral of 2011
    Tweet_1: Bobby Orr inspires Canada to win over U.S. at World Juniors: tgam.ca/DN2J (Dec 31, 2011)
    Tweet_2: Top showdowns at the parenting corral of 2011: http://tgam.ca/DNJp (Dec 29, 2011)

### Grammar

                Prep  ->  as | of | on | in | if | at | to | and
             Tweet_1  ->  A_1 Prep B_1 | Tweet_1
             Tweet_2  ->  A_2 Prep B_2 | Tweet_2
                 ...
             Tweet_N  ->  A_N Prep B_N | Tweet_N
        Frankentweet  ->  A_i Prep B_j | Tweet_i Prep B_j

## How it works

These scripts nag the feed operator by bombarding her email inbox with a subset of possible @mailandglobe frankentweets using the latest and cached @globeandmail tweets.

The operator replies to the email containing only frankentweets that she wishes to be tweeted, and the scripts tweet them for her.

### Example

    ---
    From: my@server.com
    To: my@inbox.com
    Subject: mailandglobe
    ---
    
    - @globeandmail: Marc Staal to make season debut at Winter Classic
    End of a love story? So-called gay penguins at Winter Classic
    Finland grounds high-flying Czechs at Winter Classic
    Globalive in talks to make season debut at Winter Classic
    Marc Staal to make season debut at Winter Classic and taste of misery
    Marc Staal to make season debut at Winter Classic as chosen by our photo desk
    Marc Staal to make season debut at Winter Classic at the parenting corral of 2011
    Marc Staal to make season debut at Winter Classic if woman can testify wearing niqab in sexual assault case
    Marc Staal to make season debut at Winter Classic if you want, but dont ban the niqab
    Marc Staal to make season debut at Winter Classic if you're short on cash.
    Marc Staal to make season debut at Winter Classic in democracy for N.Korea
    Marc Staal to make season debut at Winter Classic of 2011 by using Today: Canadian activists put out a simple
    Marc Staal to make season debut at Winter Classic on Israel could come back to haunt him
    Marc Staal to make season debut at Winter Classic to a better financial outlook in
    Marc Staal to make season debut at Winter Classic to ban excessive credit card surcharges
    Marc Staal to make season debut at Winter Classic to find other puzzlers
    Marc Staal to make season debut at large on Virginia Tech campus
    Marc Staal to make season debut at the turnstiles
    Russell Brand, Katy Perry to make season debut at Winter Classic
    Selanne cheered in return to make season debut at Winter Classic
    Warm reception for Howard at Winter Classic

    ---
    From: my@inbox.com
    To:   my@server.com
    Subject: re: mailandglobe
    ---

    > End of a love story? So-called gay penguins at Winter Classic

## Installation Instructions

1. Make sure the computer you are running this on can send (SMTP) and receive email (e.g., Exim)
2. Grab code
3. Install [python-twitter](http://code.google.com/p/python-twitter/)
4. Install `simplejson` and `pyyaml` (using [pip](http://pypi.python.org/pypi/pip))
5. Add an application to your Twitter account (see below)
6. Add config.yaml (see below)
7. Test scripts by running `tweets.sh` and `mail.sh`
8. Add cron jobs (below) to crontab

### Twitter app

Follow [these instructions](https://dev.twitter.com/docs/auth/tokens-devtwittercom) to allow API access to your Twitter account. Make sure to allow "Read and Write" access.

### config.yaml

Copy and paste this into config.yaml in your code directory.

    twitter:
        consumer_key: findit
        consumer_secret: findit
        access_token: findit
        access_token_secret: findit
        scrape_screen_name: globeandmail
        
        number_of_tweets: 2000
    
    mail:
        mailbox_file: /path/to/unix/mbox
        client_address: my@inbox.com
        server_address: my@server.com
        subject_line: mailandglobe
        last_check_file: lastCheck

### cron

    # @mailandglobe
    # generate possible frankentweets on the hour
    # publish frakentweets on the half hour
    0 * * * *    /root/workspace/mailandglobe/tweets.sh
    30 * * * *   /root/workspace/mailandglobe/mail.sh

### Known to work on

- a Linode share running Ubuntu 10.04
- using Python 2.6.5


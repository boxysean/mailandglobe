import twitter
import yaml

config = yaml.load(file("./config.yaml"))
tw = config["twitter"]

# See https://dev.twitter.com/docs/auth/tokens-devtwittercom to understand how to get these

api = twitter.Api(tw["consumer_key"], tw["consumer_secret"], tw["access_token"], tw["access_token_secret"])

print api.VerifyCredentials()


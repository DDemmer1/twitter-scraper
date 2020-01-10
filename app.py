#!/usr/bin/python
# -*- coding: utf-8 -*-

from flask import Flask, make_response
import requests
import tweepy
import json
import os
from flask import request

app = Flask(__name__)

consumer_key = ''
consumer_secret = ''
access_token = ''
access_token_secret = ''
scraper_controller_url = [os.environ['SCRAPER_CONTROLLER_URL']]


class MyStreamListener(tweepy.StreamListener):
    exit_stream = False
    hashtag = ""

    def set_hashtag(self, hashtag):
        self.hashtag = hashtag

    def get_hashtag(self):
        return self.hashtag

    def on_status(self, status):
        if self.exit_stream is True:
            return False

        if "RT @" not in status.text and status.in_reply_to_status_id is None:
            text = ""
            if status.truncated:
                text = status.extended_tweet['full_text']
            else:
                text = status.text

            payload = {"id": status.id,
                       "text": text,
                       "tweet_url": "https://twitter.com/i/web/status/" + status.id_str,
                       "created_at": status.timestamp_ms,
                       "lang": status.lang,
                       "user_id": status.user.id,
                       "user_profile_image_url": status.user.profile_image_url,
                       "user_handle": status.user.screen_name,
                       "user_name": status.user.name}

            headers = {'content-type': 'application/json'}
            # requests.post("http://localhost:8080/twitter/tweet/add", data=json.dumps(payload), headers=headers)
            requests.post(scraper_controller_url[0] + "/twitter/tweet/add", data=json.dumps(payload), headers=headers)

    def close_stream(self):
        self.exit_stream = True


auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

streams_set = set()


@app.route('/track/add/<string:hashtag>')
def add_track(hashtag):
    languages = []
    if request.args.get("languages") is not None:
        languages = request.args.get("languages").split(",")
    stream_listener = MyStreamListener()
    stream_listener.set_hashtag(hashtag)
    stream = tweepy.Stream(auth=api.auth, listener=stream_listener, filter_level='medium')
    stream.filter(track=['#' + hashtag], languages=languages, is_async=True)
    streams_set.add(stream_listener)
    return make_response(hashtag + ' is now tracked', 200)


@app.route('/track/close/<string:hashtag>')
def close_all(hashtag):
    for s in streams_set:
        if s.get_hashtag() == hashtag:
            s.close_stream()

    return make_response('Streams closed', 200)


if __name__ == '__main__':
    app.run()

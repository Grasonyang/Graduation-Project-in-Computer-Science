from twikit import Client, TooManyRequests
import time
from datetime import datetime
import csv
from random import randint
from configparser import ConfigParser
import asyncio
import re

# authenticate using cookies
client = Client(language='en')
client.load_cookies('cookies.json')

# data storage
with open('tweets.csv', 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['Tweet_count', 'Tweet ID', 'User Name', 'User ID', 'Text', "Link",
                    'Created_at', 'Likes', 'Retweets'])

# get tweets
MINIMUM_TWEETS = 5
PRODUCT = 'TOP'
QUERY = 'ELON'


async def get_tweets():
    tweet_count = 0
    tweets = None
    while tweet_count < MINIMUM_TWEETS:
        try:
            if tweets is None:
                print('getting tweet...')
                tweets = await client.search_tweet(QUERY, PRODUCT)
            else:
                wait_time = randint(5, 10)
                print(f'getting next tweet after {wait_time} seconds...')
                time.sleep(wait_time)
                tweets = await tweets.next()

            if not tweets:
                print('No more tweet...')
                break

            for tweet in tweets:
                tweet_count += 1
                # username clean
                username = re.sub(r'[^\w\s]', '',
                                  tweet.user.name).strip()
                # url clean
                url_match = re.search(r'https?://\S+', tweet.text)
                url = url_match.group() if url_match else None
                text_clean1 = re.sub(r'https?://\S+', '', tweet.text).strip()
                text_cleaned = re.sub(r'[^\w\s]', '', text_clean1)
                print(f'{tweet.reply_count}')
                tweet_data = [tweet_count, tweet.id, username, tweet.user.id, text_cleaned, url,
                              tweet.created_at, tweet.favorite_count, tweet.retweet_count]
                with open('tweets.csv', 'a', newline='') as file:
                    writer = csv.writer(file)
                    writer.writerow(tweet_data)

            print(f'Got {tweet_count} tweets...')
        except TooManyRequests as e:
            rate_limit = datetime.fromtimestamp(e.rate_limit_reset)
            wait_time = rate_limit - datetime.now()
            time.sleep(wait_time.total_seconds())
            print(f'Too many requests. Waiting for {wait_time} minutes.')
            continue

    print(f'Endding')

asyncio.run(get_tweets())

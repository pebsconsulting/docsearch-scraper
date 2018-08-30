# Imports the Google Cloud client library
from google.cloud import pubsub_v1
from dotenv import load_dotenv
import os
import time
import itertools


def callback(message):
    print('Received message: {}'.format(message.data))
    if message.attributes:
        print('Attributes:')
        for key in message.attributes:
            value = message.attributes.get(key)
            print('{}: {}'.format(key, value))
    message.ack()


def isEmpty(iterable):
    my_iter = itertools.islice(iterable, 0)
    try:
        my_iter.next()
    except StopIteration:
        return True
    return False


subscription_name = 'regular_consumer'
env_file = os.getcwd() + '/.env'
load_dotenv(env_file)

# Instantiates a google pub/sub client
subscriber = pubsub_v1.SubscriberClient()
publisher = pubsub_v1.PublisherClient()

GOOGLE_CLOUD_PROJECT_ID = os.environ.get('GOOGLE_CLOUD_PROJECT_ID', None)
GOOGLE_CLOUD_TOPIC = os.environ.get('GOOGLE_CLOUD_TOPIC', None)

# The resource path for the new topic contains the project ID
# and the topic name.
topic_path = subscriber.topic_path(
    GOOGLE_CLOUD_PROJECT_ID, GOOGLE_CLOUD_TOPIC)

subscription_path = subscriber.subscription_path(
    GOOGLE_CLOUD_PROJECT_ID, subscription_name)

# We have no warning if we subscribe to a subscription not created. Manual check
if isEmpty(publisher.list_topic_subscriptions(topic_path)):
    print('No subscription to the topic  {}, we will create one'.format(topic_path))

    subscription = subscriber.create_subscription(
        subscription_path, topic_path)
    print('Subscription created: {}'.format(subscription))

subscriber.subscribe(subscription_path, callback=callback)

print('Listening for messages on {}'.format(subscription_path))
while True:
    time.sleep(60)

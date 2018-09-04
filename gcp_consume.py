# Imports the Google Cloud client library
from google.cloud import pubsub_v1
from google.api_core import exceptions
from dotenv import load_dotenv
import os
import time




def callback(message):
    print('Received message: {}'.format(message.data))
    if message.attributes:
        print('Attributes:')
        for key in message.attributes:
            value = message.attributes.get(key)
            print('{}: {}'.format(key, value))
    message.ack()


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
try:
    subscriber.create_subscription(
        subscription_path, topic_path)
except exceptions.AlreadyExists:
    print('Subscription {} already exist, no need to create'.format(subscription_path))
else:
    print('Subscription {} created, note that it will not be related to the previous one'.format(subscription_path))


subscriber.subscribe(subscription_path, callback=callback)

print('Listening for messages on {}'.format(subscription_path))
while True:
    time.sleep(60)

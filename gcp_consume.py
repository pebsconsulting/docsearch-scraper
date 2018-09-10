# Imports the Google Cloud client library
from google.cloud import pubsub_v1
from google.api_core import exceptions
from dotenv import load_dotenv
import os
import time
import json

lock = False


def exec_shell_command(arguments, env=None):
    if env is None:
        env = {}
    merge_env = os.environ.copy()
    merge_env.update(env)

    from subprocess import Popen
    p = Popen(arguments, env=merge_env)
    try:
        p.wait()
    except KeyboardInterrupt:
        p.kill()
        p.wait()
        p.returncode = 1

    return p.returncode


def callback(message):
    global lock
    print('Received message: {}'.format(json.loads(message.data)['index_name']))
    # if message.attributes:
    #     print('Attributes:')
    #     for key in message.attributes:
    #         value = message.attributes.get(key)
    #         print('{}: {}'.format(key, value))

    print "lock"
    print lock

    if not (lock):
        lock = True
        message.ack()
        print json.loads(message.data)['index_name']
        exec_shell_command(["docker", "stop", "documentation-scrapper-dev"])
        exec_shell_command(["docker", "rm", "documentation-scrapper-dev"])

        run_command = [
            'docker',
            'run',
            '-e',
            'APPLICATION_ID=' + os.environ.get('APPLICATION_ID'),
            '-e',
            'API_KEY=' + os.environ.get('API_KEY'),
            '-e',
            "CONFIG=" + message.data,
            '-v',
            os.getcwd() + '/scraper/src:/root/src',
            '--name',
            'documentation-scrapper-dev',
            '-t',
            'algolia/documentation-scrapper-dev',
            '/root/run'
        ]

        print ('Running shel returned : {}'.format(exec_shell_command(run_command)))
        lock = False


subscription_name = 'regular_consumer'
env_file = os.getcwd() + '/.env'
load_dotenv(env_file)

# Instantiates a google pub/sub client
subscriber = pubsub_v1.SubscriberClient()

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


# Blocks the thread while messages are coming in through the stream. Any
# exceptions that crop up on the thread will be set on the future.
subscription = subscriber.subscribe(subscription_path, callback=callback)

print('Listening for messages on {}'.format(subscription_path))
try:
    # When timeout is unspecified, the result method waits indefinitely.
    subscription.result(timeout=300)
except Exception as e:
    print(
        'Listening for messages on {} threw an Exception: {}.'.format(
            subscription_name, e))

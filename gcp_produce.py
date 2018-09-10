# Imports the Google Cloud client library
from google.cloud import pubsub_v1
from dotenv import load_dotenv
import os
import json
from subprocess import check_output
import datetime


def callback(message_future):
    if message_future.exception():
        print('Publishing message on {} threw an Exception {}.'.format(message_future, message_future.exception()))
    else:
        print(message_future.result())


env_file = os.getcwd() + '/.env'
load_dotenv(env_file)

# Instantiates a google pub/sub client
publisher = pubsub_v1.PublisherClient()

GOOGLE_CLOUD_PROJECT_ID = os.environ.get('GOOGLE_CLOUD_PROJECT_ID', None)
GOOGLE_CLOUD_TOPIC = os.environ.get('GOOGLE_CLOUD_TOPIC', None)

# The resource path for the new topic contains the project ID
# and the topic name.
topic_path = publisher.topic_path(
    GOOGLE_CLOUD_PROJECT_ID, GOOGLE_CLOUD_TOPIC)

# message = publisher.publish(topic_path, b'config.')
# print('Topic created: {}'.format(message))

# Fetching the configuration in order to produce meassages from it

config_deployed_folder = os.environ.get('PUBLIC_CONFIG_DEPLOYED_FOLDER')
config_deployed_folder = os.path.join(config_deployed_folder, 'configs')

if not os.path.isdir(config_deployed_folder):
    print("Folder: " + config_deployed_folder + " does not exist")
    config_deployed_folder = os.path.split(config_deployed_folder)[0]
    if not os.path.isdir(config_deployed_folder):
        check_output(['mkdir', config_deployed_folder])
    check_output(['git', 'clone', 'git@github.com:algolia/docsearch-configs.git', '.'], cwd=config_deployed_folder)
    config_deployed_folder = os.path.join(config_deployed_folder, 'configs')

check_output(['git', 'pull', '-r', 'origin', 'master'], cwd=config_deployed_folder)

# Iterating through these configurations

# for configuration_filename in os.listdir(config_deployed_folder):
for index, configuration_filename in enumerate(os.listdir(config_deployed_folder), start=0):
    if '.json' in configuration_filename and index < 2:
        with open(os.path.join(config_deployed_folder, configuration_filename)) as c:
            configuration = json.load(c)
            message_future = publisher.publish(topic_path, json.dumps(configuration, indent=2, separators=(',', ': ')),
                                               origin='produce',
                                               date=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            message_future.add_done_callback(callback)

# r =requests.get('https://api.github.com/repos/algolia/docsearch-configs/contents/configs', auth=requests.auth.HTTPBasicAuth('user', 's-pace:111GitHub&*+'))
# print(r.status_code)
# print(r.json())


# # Add messages to the queue
# configs.each do |config|
#   config_name = File.basename(config['name'], '.json')
#   topic.publish config_name
# end

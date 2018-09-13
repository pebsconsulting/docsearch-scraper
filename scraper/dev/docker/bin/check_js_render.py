import json
import os
import sys
import re
import requests

conf = os.environ.get('CONFIG', None)
url = 'https://api.github.com/repos/algolia/docsearch-configs/contents/configs/' + conf + '.json'
headers = {'Accept': 'application/vnd.github.VERSION.raw'}
raw_content_response = requests.get(url, headers=headers)
nb_request_remaining = raw_content_response.headers["X-RateLimit-Remaining"]
print('\nOnly {} request(s) remaining to GitHub'.format(nb_request_remaining))
config = raw_content_response.json()
group_regex = re.compile("\\(\?P<(.+?)>.+?\\)")
results = re.findall(group_regex, conf)

if ('js_render' in config and config['js_render']) or len(results) > 0:
    sys.exit(0)
else:
    sys.exit(1)

import logging
import sys
import requests

logger = logging.getLogger(__name__)

try:
    response = requests.get(sys.argv[1])
except requests.exceptions.ConnectionError as e:
    logger.exception('Got connection error!')
    print(-1, 'Connection Error')
else:
    print(response.status_code, response.content)

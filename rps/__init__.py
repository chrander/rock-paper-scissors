import logging

logger = logging.getLogger(__name__)
logger = logging.basicConfig(level=logging.DEBUG)

# TODO: add these things to a constants module?
class_names = ['paper', 'rock', 'scissors']
QUIT = 'QUIT'
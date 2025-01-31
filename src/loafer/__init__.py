import logging

# Set up logging to ``/dev/null`` like a library is supposed to.
# https://docs.python.org/3/howto/logging.html#configuring-logging-for-a-library
logging.getLogger(__name__).addHandler(logging.NullHandler())

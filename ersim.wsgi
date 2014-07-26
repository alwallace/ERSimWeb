#!/usr/bin/python
import sys
import logging
logging.basicConfig(stream=sys.stderr)
sys.path.insert(0, "/var/www/ersim/")

from ersim import app as application
application.secret_key = '\x977n\xfcrG4\x06\xed\xf0\xd3\'\x1dh"Q\xc4\xc0\n\xf0\xd9i_\xd4'

# coding: utf-8
"""
Module for loading, updating, saving _configuration
"""

from Crypto.Cipher import Blowfish as crypto
import simplejson as json
from getpass import getpass

_config = {}

def _get_passphrase(confirm=False, length_req=15, prompt="Passphrase"):
    """Get a passphrase, loop until we get what we want"""
    while True:
        p1 = getpass(prompt + ": ")

        if len(p1) < length_req:
            print "ERROR: Phrase must be longer than %d characters" % length_req
            continue

        if confirm == False:
            break

        p2 = getpass("Repeat: ")
        if p1 == p2:
            break

        print "ERROR: Entries do not match"

    return p1

def load(filename):
    crypt = crypto.new(_get_passphrase(length_req=0, prompt="Config passphrase"), crypto.MODE_ECB)
    with open(filename, 'r') as cfg_file:
        _config.update(json.loads(crypt.decrypt(cfg_file.read())))

def save(filename):
    crypt = crypto.new(_get_passphrase(confirm=True, prompt="Config passphrase"), crypto.MODE_ECB)
    s = json.dumps(_config)
    padded_size = len(s) + (crypto.block_size - len(s) % crypto.block_size)
    with open(filename, 'w') as cfg_file:
        cfg_file.write(crypt.encrypt(s.ljust(padded_size)))

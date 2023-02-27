#!/usr/bin/env python3
import json
import logging
import sys
from logging import Formatter
from copy import copy
import hashlib

from colorama import Back
from colorama import Fore
from colorama import Style
import yaml


class ColoredFormatter(Formatter):
    """ Formatter using colorama to put colors on logs. """
    MAPPING = {
        'DEBUG': (Fore.WHITE,),
        'INFO': (Fore.CYAN,),
        'WARNING': (Fore.YELLOW,),
        'ERROR': (Fore.RED,),
        'CRITICAL': (Fore.WHITE, Back.RED),
    }

    def __init__(self, patern: str, colored: bool = True) -> None:
        Formatter.__init__(self, patern)
        self.use_color = colored

    def format(self, record) -> str:
        colored_record = copy(record)
        if self.use_color:
            levelname = colored_record.levelname
            seq: tuple = self.MAPPING.get(levelname, tuple())
            colored_levelname = ''
            for i in seq:
                colored_levelname += i
            colored_levelname += levelname + Style.RESET_ALL
            colored_record.levelname = colored_levelname
        return Formatter.format(self, colored_record)


logger = logging.getLogger('gh-trufflehog')
stream_handler = logging.StreamHandler(sys.stderr)
stream_handler.setFormatter(
    ColoredFormatter(
        '%(levelname)s :: %(name)s :: %(message)s',
        colored=True,
    ),
)
stream_handler.setLevel(logging.INFO)
logger.setLevel(logging.INFO)
logger.addHandler(stream_handler)
logger.propagate = True


def wrapper():
    # Open whitelists
    whitelists = {}
    try:
        with open('.trufflehog_whitelist.yaml', encoding='utf-8') as fc:
            data = yaml.safe_load(fc)
            for wl in data['whitelist']:
                whitelists[wl['secret']] = wl['reason']
    except FileNotFoundError:
        logger.warning("No whitelist found.")
    # Filter output
    filtered = []
    with open('output.json', encoding='utf-8') as fc:
        for line in fc:
            data = json.loads(line)
            file = data['SourceMetadata']['Data']['Git']['file']
            line = data['SourceMetadata']['Data']['Git']['line']
            kind = data['DetectorName']
            secret = data['Raw']
            secret = secret.replace('\n', '')
            if secret in whitelists:
                logger.debug("file=%s,line=%s::%s secret whitelisted", file, line, kind)
                continue
            filtered.append(data)
            logger.error("file=%s,line=%s::%s secret leaked! (%s)", file, line, kind, secret)
    # Dump filtered output
    with open('output_filtered.json', 'w', encoding='utf-8') as fc:
        for element in filtered:
            fc.write(json.dumps(element) + '\n')
    # Exit error
    if len(filtered) > 0:
        exit(2)


if __name__ == '__main__':
    wrapper()

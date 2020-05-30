from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import sys
import time

from google.cloud import translate_v2

from ..debug import log
from ..util.opt import Opt

_translate_client = translate_v2.Client()
_langs = _translate_client.get_languages()


def translate_text(text, target_lang='en', source_lang=None):
    if text is None or len(text) < 1:
        text = ''
        return Opt(trans=''.encode('utf-8'), src=text.encode('utf-8'))

    translation = _translate_client.translate(
        text,
        target_language=target_lang,
        source_language=source_lang)
    return Opt(trans=translation['translatedText'].encode('utf-8'), src=translation['input'].encode('utf-8'))


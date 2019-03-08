import os
import random
import datetime
import pytz
from hashlib import md5
from django.conf import settings


def image_path(instance, filename):
    """Generates likely unique image path using md5 hashes"""
    filename, ext = os.path.splitext(filename.lower())
    instance_id_hash = md5(str(instance.id)).hexdigest()
    filename_hash = ''.join(random.sample(md5(filename.encode('utf-8')).hexdigest(), 8))
    return '{}/{}{}'.format(instance_id_hash, filename_hash, ext)


def check_now():
    tz = pytz.timezone(settings.TIME_ZONE)
    return datetime.datetime.now(tz)

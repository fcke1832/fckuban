import os
import random
from hashlib import md5

def image_path(instance, filename):
    """Generates likely unique image path using md5 hashes"""
    filename, ext = os.path.splitext(filename.lower())
    instance_id_hash = md5(str(instance.id)).hexdigest()
    filename_hash = ''.join(random.sample(md5(filename.encode('utf-8')).hexdigest(), 8))
    return '{}/{}{}'.format(instance_id_hash, filename_hash, ext)

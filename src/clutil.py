#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Author:
    Copyright Oliver Vinn 2015
Repo:
    github.com/ovinn/code-lytics
"""
import os
import re
import hashlib

def sizeof_fmt(num, suffix='B'):
    """
    Format a number to a string with appropriate data size units
    """
    for unit in ['', 'Ki', 'Mi', 'Gi', 'Ti', 'Pi', 'Ei', 'Zi']:
        if abs(num) < 1024.0:
            return '%3.1f%s%s' % (num, unit, suffix)
        num /= 1024.0
    return '%.1f%s%s' % (num, 'Yi', suffix)

def file_condition_cnt(filename):
    """
    Counts number of #if instances in a file
    """
    content = open(filename).read()
    return len(re.findall('#if', content))

def file_source_size(filename):
    """
    Gets the byte size of a file
    """
    return os.path.getsize(filename)

def fingerprint_file(filename):
    """
    Hashes file content to produce a unique fingerprint
    """
    hasher = hashlib.sha1()
    block_size = 65536
    with open(filename, 'rb') as file_to_hash:
        buf = file_to_hash.read(block_size)
        while len(buf) > 0:
            hasher.update(buf)
            buf = file_to_hash.read(block_size)
    return hasher.hexdigest()

def find_files(path, ext='*.*'):
    """
    Gets a list files under a path that match the given extension
    """
    lst_matches = []
    for root, dirs, files in os.walk(path):
        for file in files:
            if file.endswith(ext):
                lst_matches.append(os.path.join(root, file))
    return  lst_matches

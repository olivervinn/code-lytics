#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Author:
    Copyright Oliver Vinn 2015
Repo:
    github.com/ovinn/code-lytics
"""

import json
import urllib
import logging

class Jenkins(object):
    """
    Jenkins access container providing access to supported features
    """
    def __init__(self, url, log=False, job=None):
        """
        Create jenkins service instance to pull information

        Args:
            url (str):   url to a jenkins master
            log (bool):  True to enable sterr messages
        """
        self.url = url
        self.log = log
        self.job = job
        self.build_number = None

    def __decode_warnings(self, warnings):
        warn = dict()
        total = 0
        for warning in warnings:
            if warning['primaryLineNumber'] > -1:
                name = warning['fileName']
                logging.info('Jenikins issue: ' + name)
                if name not in warn.keys():
                    warn[name] = []
                url = self.url + self.job + '/' + str(self.build_number)
                url = url + '/warnings30Result/source.'
                url = url + str(warning['key']) + "#" + str(warning['primaryLineNumber'])
                warn[name].append({'url': url,
                                   'line': warning['primaryLineNumber'],
                                   'message' : warning['message']})
                total += 1
        return warn

    def fetch_latest_warnings(self, job=None):
        """
        Fetch last build warnings for job.

        Args:
            job (str):           name of jenkins job
            path_divider (str):  path divider for workspace

        Returns:
            Dictionary of files with warning count
        """

        if not job:
            self.job = job

        # Get build number
        url = self.url + job + '/api/json?depth=1'
        logging.info('Connecting to ' + url)
        response = urllib.urlopen(url)
        raw = response.read()
        logging.info('Received data size of ' + str(len(raw)))
        data = json.loads(raw)
        self.build_number = data['lastCompletedBuild']['number']

        # Build url
        url = self.url + job + '/' + str(self.build_number)
        url = url + '/warningsResult/api/json?pretty=true&depth=1'

        # Now get results
        response = urllib.urlopen(url)
        raw = response.read()
        logging.info('Received data size of ' + str(len(raw)))
        data = json.loads(raw)
        return self.__decode_warnings(data['warnings'])

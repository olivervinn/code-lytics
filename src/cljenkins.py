#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright Oliver Vinn 2015
# github.com/ovinn/proj-lytics

import sys
import os
import json
import urllib
from collections import defaultdict

class Jenkins:
    def __init__(self, url, log=False):
        '''
        Create jenkins service instance to pull information

        Args:
            url (str):   url to a jenkins master
            log (bool):  True to enable sterr messages
        '''
        self.url = url
        self.log = log

    def fetch_latest_warnings(self, job):
        '''
        Fetch last build warnings for job.

        Args:
            job (str):           name of jenkins job
            path_divider (str):  path divider for workspace

        Returns:
            Dictionary of files with warning count
        '''
        # Get build number
        url = self.url + job + "/api/json?depth=1"
        self.job = job
        self.__log("Connecting to " + url)
        response = urllib.urlopen(url);
        raw = response.read()
        self.__log("  " + "Received data size of " + str(len(raw)))
        data = json.loads(raw)
        self.build_number = data['lastCompletedBuild']['number']
        # Now get results
        url = self.url + job + "/" + str(self.build_number) + "/warningsResult/api/json?pretty=true&depth=1"
        response = urllib.urlopen(url);
        raw = response.read()
        self.__log("  " + "Received data size of " + str(len(raw)))
        data = json.loads(raw)
        return self.__decode_warnings(data["warnings"])

    def __log(self, message):
        if self.log:
            sys.stderr.write(message + '\n')

    def __decode_warnings(self, warnings):
        warn = dict()
        total = 0
        for w in warnings:
            if w["primaryLineNumber"] > -1:
                name = w["fileName"]
                self.__log("Jenikins issue: %s\n" %name)
                if name not in warn.keys():
                    warn[name] =  []
                warn[name].append({'url': 
                                 self.url + 
                                 self.job + '/' +
                                 str(self.build_number) + "/warnings30Result/source." + str(w['key']) + "#" +
                                 str(w['primaryLineNumber']), 
                                 'line': w['primaryLineNumber'],
                                 'message' : w['message']})
                total += 1
        return warn

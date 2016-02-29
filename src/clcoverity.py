#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Author:
    Copyright Oliver Vinn 2015

Repo:
    github.com/ovinn/code-lytics
"""
from suds.client import Client
from suds.wsse import *
import os
import logging

class Coverity(object):
    """
    Coverit instance
    """
    class IssueInfo(object):
        """
        Container for a coverity issue
        """
        def __init__(self, cid, filepath, checker, function, url):
            """
            Supported arguments
            """
            self.cid, self.filepath, self.checker, self.function = cid, filepath, checker, function
            self.url = url

    def __init__(self, url, user, password):
        """
        Create connection to a coverity instance operating with v7 API

        Args:
            url (str):      base url
            user (str):     username to authenticate with
            password (str): users paswword
        """
        self.url = url
        self.wsdlurl_defect = url + '/ws/v7/defectservice?wsdl'
        self.client = Client(self.wsdlurl_defect)

        self.wsdlurl_cfg = url + '/ws/v7/configurationservice?wsdl'
        self.client_cfg = Client(self.wsdlurl_cfg)

        self.security = Security()
        token = UsernameToken(user, password)
        self.security.tokens.append(token)
        self.client.set_options(wsse=self.security)
        self.client_cfg.set_options(wsse=self.security)

    def fetch_component_map(self, component_map):
        """
        Gets the component map which descibes the regex rules for
        placing code in a specific named group

        Args:
            component_map (str):      name of map
        """
        filter_spec = self.client_cfg.factory.create('componentMapFilterSpecDataObj')
        filter_spec.namePattern = component_map
        c_map = self.client_cfg.service.getComponentMaps([filter_spec])
        groups = []
        for rule in c_map[0].componentPathRules:
            groups.append({'rule' : rule.pathPattern, 'component' : rule.componentId.name})
        return groups

    def fetch_project_stats(self, project_name):
        """
        Gets code statastics for the project. Grouped into component data

        Args:
            project_name
        """
        component_stats = dict()
        spec = self.client.factory.create('projectIdDataObj')
        spec.name = project_name
        logging.info('Fetching project stats')
        metrics = self.client.service.getComponentMetricsForProject(spec)
        for metric in metrics:
            component_stats[metric.componentId.name] = metric.codeLineCount
        return component_stats

    def fetch_open_defects(self, project_name, stream_name):
        """
        Fetch outstanding issues on a stream

        Args:
            project_name (str): Exact project name
            stream_name (str):  Exact stream name
        """
        filter_spec = self.client_cfg.factory.create('projectFilterSpecDataObj')
        filter_spec.namePattern = project_name
        c_projects = self.client_cfg.service.getProjects([filter_spec])
        project_id = c_projects[0].projectKey
        project_id_obj = self.client.factory.create('projectIdDataObj')
        project_id_obj.name = project_name

        stream_id_list = self.client.factory.create('streamIdDataObj')
        stream_id_list.name = stream_name
        filter_spec = self.client.factory.create('streamDefectFilterSpecDataObj')
        filter_spec.includeHistory = False
        filter_spec.includeDefectInstances = True
        filter_spec.streamIdList = [stream_id_list]

        pagespec = self.client.factory.create('pageSpecDataObj')
        pagespec.pageSize = 2000

        fspec = self.client.factory.create('mergedDefectFilterSpecDataObj')
        fspec.statusNameList = ['New', 'Triaged']

        cids = self.client.service.getMergedDefectsForStreams(stream_id_list, [fspec], pagespec)

        issues = []
        for issue in cids.mergedDefects:
            funname = '' if 'functionName' not in issue.__dict__ else issue.functionName
            url = self.url + '/sourcebrowser.htm?projectId='
            url = url + str(project_id) + '&mergedDefectId=' + str(issue.cid)
            issues.append(Coverity.IssueInfo(issue.cid,
                                             issue.filePathname.replace(os.path.sep, '/'),
                                             issue.checkerName,
                                             funname,
                                             url))
        return issues

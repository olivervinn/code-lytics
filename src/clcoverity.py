#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright Oliver Vinn 2015
# github.com/ovinn/proj-lytics

from suds.client import Client
from suds.wsse import *
import logging

# logging.basicConfig(level=logging.INFO)

class Coverity:

    class IssueInfo:
        def __init__(self, cid, filepath, checker, function, url):
            self.cid, self.filepath, self.checker, self.function  = cid, filepath, checker, function
            self.url = url
            
        def __str__(self):
            return ("%s, %s" %(self.cid, self.filepath))

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
        filterSpec = self.client_cfg.factory.create("componentMapFilterSpecDataObj")
        filterSpec.namePattern = component_map
        c_map = self.client_cfg.service.getComponentMaps([filterSpec])
        groups = []
        for c in c_map[0].componentPathRules:
            groups.append({'rule' : c.pathPattern, 'component' : c.componentId.name})
        return groups

    def fetch_project_stats(self, project_name, component_map):
        spec = self.client.factory.create("projectIdDataObj")
        spec.name = project_name
        #spec_c = self.client.factory.create("componentIdDataObj")
        #spec_c.name = 
        component_stats = dict()
        c = self.client.service.getComponentMetricsForProject(spec)
        for i in c:
            component_stats[i.componentId.name] = i.codeLineCount
        return component_stats
   
    
    def fetch_outstanding_stream_defects(self, project_name, stream_name):
        """
        Fetch outstanding issues on a stream

        Args:
            project_name (str): Exact project name
            stream_name (str):  Exact stream name
        """
        filterSpec = self.client_cfg.factory.create("projectFilterSpecDataObj")
        filterSpec.namePattern = project_name
        c_projects = self.client_cfg.service.getProjects([filterSpec])
        self.project_id = c_projects[0].projectKey
        
        projectID = self.client.factory.create("projectIdDataObj")
        projectID.name = project_name

        filterSpec = self.client.factory.create("streamDefectFilterSpecDataObj")
        filterSpec.includeHistory = False
        filterSpec.includeDefectInstances = True
        streamIdList = self.client.factory.create("streamIdDataObj")
        streamIdList.name = stream_name
        filterSpec.streamIdList = [streamIdList]

        pagespec = self.client.factory.create("pageSpecDataObj")
        pagespec.pageSize = 2000

        fspec = self.client.factory.create("mergedDefectFilterSpecDataObj")
        fspec.statusNameList = ["New", "Triaged"]

        cids = self.client.service.getMergedDefectsForStreams(streamIdList, [fspec], pagespec)

        issues = []
        for c in cids.mergedDefects:
            f = "" if "functionName" not in c.__dict__ else c.functionName
            issues.append(Coverity.IssueInfo(c.cid, 
                                             c.filePathname.replace(os.path.sep, '/'), 
                                             c.checkerName, 
                                             f,
                                             self.url + "/sourcebrowser.htm?projectId="+str(self.project_id) +
                                             "&mergedDefectId=" + str(c.cid)))

        return issues


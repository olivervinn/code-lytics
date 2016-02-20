#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright Oliver Vinn 2015
# github.com/ovinn/proj-lytics

import os
import sys
import json
import urllib
import re
from collections import defaultdict

from cljenkins import Jenkins
from clcoverity import Coverity
import clutil
from sys import stdout

class SourceModel:
    def __init__(self, strip_paths=None):
        self.items = {}
        self.item_lookup = defaultdict(list)
        self.groups = []
        self.group_stats = []
        self.strip_paths = strip_paths

    def add_group(self, name, matches):
        '''
        Args:
            name (str) - display name
            matches (list) - regex strings to match against
        '''
        self.group.append({'rule': name, 'component' : matches})

    def add(self, item):
        for i in self.strip_paths:
            if i and item.path.startswith(i):
                item.path = item.path[len(i):]
        self.items[item.path] = item
        self.item_lookup[item.path.split('/')[-1]].append(item)

    def getitem(self, path):
        name = path.split('/')[-1]
        if name in self.item_lookup:
            subs = self.item_lookup[name]
            for i in subs:
                if path.endswith(i.path):
                    return i
        return None

class SourceItem:
    def __init__(self, path=None, name=None, component=None, module=None):
        self.path = path
        self.name = name
        self.component = component
        self.module = module
        self.compiler_issues = []
        self.coverity_issues = []
        self.misra_issues = defaultdict(list)
        if os.path.exists(path):
            self.size = clutil.file_source_size(path)
            self.conditions = clutil.file_condition_cnt(path)
        else:
            self.size = 0
            self.conditions = 0
        if path.endswith(".c"):
            self.fingerprints = {}
            self.dependson = []
            
    def __repr__(self):
        return "issues %d %d %d" %(len(self.compiler_issues), len(self.coverity_issues), len(self.misra_issues))


def mixin_dependency(args):
    '''
    '''
    d, matches = args
    for l_file in matches:
        name = os.path.basename(d['name'])
        l_name = os.path.basename(l_file)
        l_name = ".".join(l_name.split(".")[:-2])  # .o.lst
        # sys.stderr.write(" ?    " + l_name + " <==> " + name + " " + d['path'] + "\n")
        if 'fingerprints' in d:
            if l_name == name and d['component'] in l_file and d['module'] in l_file:
                p = clutil.fingerprint_file(l_file)
                if p in d['fingerprints']:
                    d['fingerprints'][p].append(l_file)
                else:
                    d['fingerprints'][p] = [ l_file ]
                matches.remove(l_file)
                sys.stderr.write("Finished " + l_file + "\n")

                for m in d['fingerprints'].values():
                    lines = open(m[0]).readlines()
                    for l in lines:
                        if l.startswith("#line 1 "):
                            d['depends-on'].append(l.strip()[9:-1])
                d['depends-on'] = list(set(d['depends-on']))

def mixin_dependencies(description, matches):
    for d in description:
        mixin_dependency((d, matches))
    return description

def mixin_compiler_warnings(source_model, warnings):
    '''
    Merge filesystem description and compiler warning data

    Args:
        description (list):
        warnings (list):
    '''
    for w in warnings.keys():
        m = None
        for d in source_model.items:
            if w.endswith(d):
                m = source_model.items[d]
                break
        if not m:
            m = SourceItem(w, w.split('/')[-1], 'Other', '')
            source_model.add(m)
        m.compiler_issues.extend(warnings[w])
    return source_model

def mixin_coverity_warnings(source_model, warnings):
    '''
    Merge filesystem description and coverity warning data

    Args:
        description (list):
        warnings (list):
    '''
    for w in warnings:
        m = None
        for d in source_model.items:
            if w.filepath.endswith(d):
                m = source_model.items[d]
                break
        if not m:
            m = SourceItem(w.filepath, w.filepath.split('/')[-1], 'Other', '')
            source_model.add(m)
        m.coverity_issues.append(w.__dict__)
    return source_model

def mixin_qac_warnings(source_model, files):
    wr = re.compile('(.*)\\((.*)\\) \\+\\+ WARNING \\+\\+: <=([7-8])=(.*)')
    sys.stderr.write("Found %s files \n" % len(files))
    for f in files:
        content = open(f).readlines()
        for line in content:
            warning_match = wr.match(line)
            if warning_match:
                warning_origin = warning_match.group(1).replace(os.path.sep, '/')
                m = source_model.getitem(warning_origin)
                if not m:
                    m = SourceItem(warning_origin, warning_origin.split('/')[-1], 'OTHER', '')
                    source_model.add(m)
                m.misra_issues[int(warning_match.group(3))].append({'line' : warning_match.group(2),
                                                                    'detail' : warning_match.group(4)})

    return source_model

def get_description(jenkins_url, jenkins_job, coverity_url, coverity_project, coverity_stream):
    '''
    Gets a rich description of the cm location agreegating file sytem and analytic sources
    '''
    from datetime import datetime

	enb_jenkins = True
    enb_coverity = True
        
    # Ensure relative path is ok
    os.chdir('..')

    # Build local source tree (list paths to be stripped)
    cm = SourceModel(['<mypath>',
                      '<another>'])
    
	sys.stderr.write("Scanning local QAC data \n")
    a = datetime.now()
    cm = mixin_qac_warnings(cm, clutil.find_files('build\\output\\', '.qac'))

    if enb_jenkins:
        b = datetime.now() - a
        sys.stderr.write(str(b) +  "\nFetching Jenkins Data from Server\n")
        a = datetime.now()
        j = Jenkins(jenkins_url)
        jd = j.fetch_latest_warnings(jenkins_job)
        sys.stderr.write("\n".join([str(x) for x in jd]))
        sys.stderr.write("Total: %d\n" %(len(jd)))
        
    if enb_coverity:
        b = datetime.now() - a
        sys.stderr.write(str(b) + "\nFetching Coverity Data from Server \n")
        a = datetime.now()
        c = Coverity(coverity_url, 'USER', 'PASS')
        cm.groups = c.fetch_component_map('MAPPING')
        cm.group_stats = c.fetch_project_stats(coverity_project, cm.groups)
        cd = c.fetch_outstanding_stream_defects(coverity_project, coverity_stream)
        sys.stderr.write("\n".join([str(x) for x in cd]))
        sys.stderr.write("Total: %d\n" %(len(cd)))
        
    if enb_jenkins:
        b = datetime.now() - a
        sys.stderr.write(str(b) +  "\nMerging Compiler Data\n")
        a = datetime.now()
        cm = mixin_compiler_warnings(cm, jd)
    
    if enb_coverity:
        b = datetime.now() - a
        sys.stderr.write(str(b) +  "\nMerging Coverity Data\n")
        a = datetime.now()
        cm = mixin_coverity_warnings(cm, cd)
        b = datetime.now() - a
        sys.stderr.write(str(b))
        
    return cm

if __name__ == "__main__":

    J_URL    = 'https://jenkins/jenkins/job/'
    J_JOB    = 'Test'
    C_URL    = 'http://coverity:8080'
    C_PROJ   = 'Ford_GEN4'
    C_STREAM = 'B515_NIGHTLY'

    model = get_description(J_URL, J_JOB, C_URL, C_PROJ, C_STREAM)

    groups = model.groups
    groups.append({'component' : 'OTHER', 'rule' : re.compile('.*')})

    # group
    #   name: component
    #   files:    files
    
    for k in groups:
        k['rule'] = re.compile(k['rule'])
    
    items = defaultdict(list)
    for d,v in model.items.items():
        for k in groups:
            if k['rule'].match(d):
                items[k['component']].append(v)
                break;

    # Add empty component groups
    for i in groups:
        if i['component'] not in items.keys():
            items[i['component']] = []

    # Sorted order
    names = sorted(items.keys())
    out = [{'name': x, 'files' : [y.__dict__ for y in items[x]]} for x in names]

    print(json.dumps({'data': out, 'stats' : model.group_stats }))
 
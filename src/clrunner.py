#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Merges data sources into a code-lytics dataset

Autor:
    Copyright Oliver Vinn 2015
Repo:
    github.com/ovinn/code-lytics
"""

import os
import sys
import re
from collections import defaultdict

from cljenkins import Jenkins
from clcoverity import Coverity
import clutil

class SourceModel:
    """
    Container for a set of source files
    """
    def __init__(self, strip_paths=None):
        """
        Args:
            strip_paths (list(str))    - List of strings to remove from start of file path
        """
        self.items = {}
        self.item_lookup = defaultdict(list)
        self.groups = []
        self.group_stats = []
        self.strip_paths = strip_paths

    def add_group(self, name, matches):
        """
        Defines a new source grouping rule

        Args:
            name (str) - display name
            matches (list) - regex strings to match against
        """
        self.groups.append({'rule': name, 'component' : matches})

    def add(self, item):
        """
        Adds new item to the collection

        Args:
            item (SourceItem) - Source item (file) to add to the collection
        """
        # Strip string from path
        for i in self.strip_paths:
            if i and item.path.startswith(i):
                item.path = item.path[len(i):]
        # General collection
        self.items[item.path] = item
        # Add for faster lookup in large collections
        self.item_lookup[item.path.split('/')[-1]].append(item)

    def getitem(self, path):
        """
        Gets the requested source item

        Args:
            path - full filename of a file to retrieve

        Returns:
            SourceItem if found otherwise None
        """
        name = path.split('/')[-1]
        if name in self.item_lookup:
            subs = self.item_lookup[name]
            for i in subs:
                if path.endswith(i.path):
                    return i
        return None

class SourceItem:
    """
    Describes a source files quality indicators
    """
    def __init__(self, path=None, name=None, component=None, module=None):
        """
        Args:
            path (str) - full filename
            name (str) - short name
            component (str) - optional direct grouping attribute
            module (str) - optional direct secondary grouping attribute
        """
        # File attributes
        self.path = path
        self.name = name
        self.component = component
        self.module = module
        # Quality attributes
        self.compiler_issues = []
        self.coverity_issues = []
        self.misra_issues = defaultdict(list)
        # Computes factors
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
        return "issues %d %d %d" %(len(self.compiler_issues),
                                   len(self.coverity_issues),
                                   len(self.misra_issues))


def mixin_dependencies(source_model, matches):
    '''
    For a given list of files that represent unique source file outcomes
    generates a unique fingerprint for comparison to determine true number
    of compile outcomes.

    Args:
        source_model (SourceModel) - source model description
        matches (list) -
    '''
    for descriptor in source_model:
        for l_file in matches:
            name = os.path.basename(descriptor['name'])
            l_name = os.path.basename(l_file)
            l_name = ".".join(l_name.split(".")[:-2])  # .o.lst
            if 'fingerprints' in descriptor:
                if l_name == name and descriptor['component'] in l_file and descriptor['module'] in l_file:
                    p = clutil.fingerprint_file(l_file)
                    if p in descriptor['fingerprints']:
                        descriptor['fingerprints'][p].append(l_file)
                    else:
                        descriptor['fingerprints'][p] = [l_file]
                    matches.remove(l_file)
                    sys.stderr.write("Finished " + l_file + "\n")

                    for m in descriptor['fingerprints'].values():
                        lines = open(m[0]).readlines()
                        for l in lines:
                            if l.startswith("#line 1 "):
                                descriptor['depends-on'].append(l.strip()[9:-1])
                    descriptor['depends-on'] = list(set(descriptor['depends-on']))
    return source_model

def mixin_compiler_warnings(source_model, warnings):
    '''
    Merge filesystem description and compiler warning data

    Args:
        source_model (SourceModel) - source model description
        warnings (list) - warnings to merge into model
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
        source_model (SourceModel) - source model description
        warnings (list) - warnings to merge into model
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
    '''
    Args:
        source_model (SourceModel) - source model description
        files (list) - warnings files to scan for issues and merge into model
    '''
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

def get_model_desc(jenkins_url, jenkins_job,
                   coverity_url, coverity_project, coverity_stream, coverity_map, user, password,
                   misra_file_search_path, misra_file_extension,
                   strip_paths,
                   include_jenkins=True,
                   include_coveritry=True):
    '''
    Gets a rich description of the cm location agreegating file sytem and analytic sources.

    Args:
        jenkins_url (str)      - base url for instance
        jenkins_job (str)      - name of job
        coverity_url (str)     - base url for instance
        coverity_project (str) - name of coverity project
        coverity_stream (str)  - name of coverity stream in project
        coverity_map (str)     - name of coverity component map
        user (str)             - user to acccess coverity
        password (str)         - users password

    Returns:
        Source Model

    Limitations:
        Minimal (no) error protection for server being down.
    '''
    from datetime import datetime

    # Build local source tree (list paths to be stripped)
    model = SourceModel(strip_paths)

    sys.stderr.write("Scanning local QAC data\n")
    a = datetime.now()
    model = mixin_qac_warnings(model, clutil.find_files(misra_file_search_path, misra_file_extension))

    if include_jenkins:
        b = datetime.now() - a
        sys.stderr.write(str(b) + "Fetching Jenkins Data from Server\n")
        a = datetime.now()
        j = Jenkins(jenkins_url)
        jd = j.fetch_latest_warnings(jenkins_job)
        sys.stderr.write("Total: %d\n" %(len(jd)))

    if include_coveritry:
        b = datetime.now() - a
        sys.stderr.write(str(b) + "Fetching Coverity Data from Server\n")
        a = datetime.now()
        c = Coverity(coverity_url, user, password)
        model.groups = c.fetch_component_map(coverity_map)
        for k in model.groups:
            k['rule'] = re.compile(k['rule'])
        model.group_stats = c.fetch_project_stats(coverity_project, model.groups)
        open_issues = c.fetch_open_defects(coverity_project, coverity_stream)
        sys.stderr.write("Total: %d\n" %(len(open_issues)))

    if include_jenkins:
        b = datetime.now() - a
        sys.stderr.write(str(b) + "Merging Compiler Data\n")
        a = datetime.now()
        model = mixin_compiler_warnings(model, jd)

    if include_coveritry:
        b = datetime.now() - a
        sys.stderr.write(str(b) + "Merging Coverity Data\n")
        a = datetime.now()
        model = mixin_coverity_warnings(model, open_issues)
        b = datetime.now() - a
        sys.stderr.write(str(b))

    model.groups.append({'component' : 'OTHER', 'rule' : re.compile('.*')})
    return model

def model_to_jsonable(model):
    """
    Convert to a json compatible data form
    """
    items = defaultdict(list)
    for d, v in model.items.items():
        for k in model.groups:
            if k['rule'].match(d):
                items[k['component']].append(v)
                break
    # Add empty component groups
    for i in model.groups:
        if i['component'] not in items.keys():
            items[i['component']] = []
    # Sorted order
    names = sorted(items.keys())
    out = [{'name': x, 'files' : [y.__dict__ for y in items[x]]} for x in names]
    return {'data': out, 'stats' : model.group_stats}

 
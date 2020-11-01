#!/usr/bin/env python

##################################################################
# must-gather rule checking tool

from __future__ import print_function
import os
import sys 
import tarfile
import tokenize
import argparse

from plugins.mustGatherAccessor import MustGatherAccessor
from plugins.xmgPlugin import XmgPlugin
from utilities.importerHelper import ImporterHelper

from transforms.events import Events
from transforms.logLevel import LogLevel
from transforms.transformJson import TransformJson
from transforms.transformYaml import TransformYaml
from transforms.transformSummary import TransformSummary
from transforms.transformClusterStatus import TransformClusterStatus

def processPlugins (accessor,memberDictionary,includeList=None,excludeList=None):
    print("Processing plugins:" , file=sys.stderr)
    plugins = XmgPlugin.enumeratePlugins(accessor,"analysis",includeList,excludeList)
    for plugin in plugins:
        print(" - " + plugin.getName() + " -", file=sys.stderr, end=" ")
        plugin.run()
        print("Done", file=sys.stderr)

def showPlugins(val=None):
    plugins = XmgPlugin.enumeratePlugins(None)
    print("Choose a Plugin from the Installed Plugins")
    print("---------------------------------------------------")
    print("Group\t\tPlugin Name")
    print("---------------------------------------------------")
    for plugin in plugins:        
        print(plugin.getGroup()+"\t"+plugin.getName())
    print("\nxmg.py -e \"plugin name\"")


def processMustGather (file,includeList,excludeList):
    members = {}        
    print("Loading must-gather archive: " + file + " - ", file=sys.stderr , end=" ")
    accessor = MustGatherAccessor(file)    
    accessor.readfile()
    print("Done", file=sys.stderr)
    processPlugins(accessor,members,includeList,excludeList)


def get_cli_args():
    def showUsage():
        parser.print_help(sys.stderr)
        sys.exit(127)
    
    def default(args):
        showUsage()

    def process_analyze(namespace):          
        minLevel = LogLevel.LEVEL_WARNING
        includeList = None        
        excludeList = None
        if "show_plugins" in namespace and namespace.show_plugins: 
            showPlugins()
            return
            
        if "full" in namespace:
            includeList = namespace.full
        
        if includeList == None:
            if "enable_plugins" in namespace:
                includeList = namespace.enable_plugins
            
            if "disable_plugins" in namespace:
                excludeList = namespace.disable_plugins

        if "level" in namespace:
            level = namespace.level.upper()
            if LogLevel.valueOf(level) == -1:
                print("Warning - level must be [INFO,WARNING,ERROR]. Defaulting to " + minLevel)
            else:
                minLevel = level
        Events.getInstance().setLogLevel(minLevel)
        
        processMustGather(namespace.analyze_archive,includeList,excludeList)             
        if "output" in namespace:
            if namespace.output == "yaml":
                TransformYaml().run()             
            elif namespace.output == "summary":
                TransformSummary(includeList).run()
            elif namespace.output == "status":
                TransformClusterStatus(includeList).run()
            else:
                TransformJson().run()
        else:
            TransformJson().run()

    parser = argparse.ArgumentParser(description='must-gather analysis tool')
    parser.set_defaults(func=default)
    
    #subparsers = parser.add_subparsers()

    analyzeParser = parser#subparsers.add_parser('analyze', help='This is used to read a must gather archive and analyze it.')
    analyzeParser.add_argument('-a', '--analyze-archive', type=str, default=None, required=False,
            help='Use this to modify the path to the mustgather archive.')
    analyzeParser.add_argument('-v', '--verbose', action='store_true',
            default=False, help='Use this flag to get extra information regarding what is being done.')
    analyzeParser.add_argument('-o', '--output', type=str, default='summary', required=False, help='Determines the output format of the report. Options are json, yaml, summary')
    analyzeParser.add_argument('-f', '--full', type=str, default=None, required=False, help='Used with the summary output to show all events associated with a plugin. ')
    analyzeParser.add_argument('-l', '--level', type=str, default='WARNING', required=False, help='The minimum log level to be included in output or a report')
    analyzeParser.add_argument('-p', '--show-plugins',  action='store_true', help='Shows all plugins')
    analyzeParser.add_argument('-e', '--enable-plugins', type=None, default=None, required=False, help='Comma separated list of plugins to enable.')
    analyzeParser.add_argument('-d', '--disable-plugins', type=None, default=None, required=False, help='Comma separated list of plugins to disbale.')
    analyzeParser.set_defaults(func=showPlugins)
    
    args = parser.parse_args()
    args.func(args)

    return args

if __name__ == "__main__":
    print("must-gather analysis utility", file=sys.stderr)
    print("---------------------------------------------------\n")
    cli_args = get_cli_args()
    #processMustGather(cli_args.archive)
    


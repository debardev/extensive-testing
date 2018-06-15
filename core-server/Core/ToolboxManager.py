#!/usr/bin/env python
# -*- coding: utf-8 -*-

# -------------------------------------------------------------------
# Copyright (c) 2010-2018 Denis Machard
# This file is part of the extensive testing project
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
# MA 02110-1301 USA
# -------------------------------------------------------------------

import base64
import zlib
import os
import subprocess
import sys
import time
import shutil

# unicode = str with python3
if sys.version_info > (3,):
    unicode = str
    
import json

try:
    import ProbeServerInterface as PSI
    import AgentServerInterface as ASI
    import EventServerInterface as ESI
    import Context
    import Common
    import ProbesManager
    import AgentsManager
except ImportError: # python3 support
    from . import ProbeServerInterface as PSI
    from . import AgentServerInterface as ASI
    from . import EventServerInterface as ESI
    from . import Context
    from . import Common
    from . import ProbesManager
    from . import AgentsManager
    
from Libs import Settings, Logger


class ToolboxManager(Logger.ClassLogger):    
    def __init__(self):
        """
        Construct toolbox Manager
        """
        self.pkgsToolsPath = "%s/%s/%s/linux2/" % ( Settings.getDirExec(),   Settings.get( 'Paths', 'packages' ), 
                                        Settings.get( 'Paths', 'tools' ) )

        self.info( 'Detecting local tools to deploy...' )
        pkg = self.preInstall()
        if Settings.getInt( 'WebServices', 'local-tools-enabled' ):
            if pkg is not None:
                self.info( 'Deploying local tools %s...' % pkg)
                self.installPkgV2(pkgName=pkg)

        self.TOOLS_INSTALLED = False
        try:
            import Toolbox
            self.TOOLS_INSTALLED = True
            self.info( "Local tools are installed" )
        except Exception as e:
            self.info( "Local tools are NOT installed" )
            self.trace( "More details: %s" % unicode(e).encode('utf-8') )
        self.configsFile = None
        self.__pids__ = {}

    def preInstall(self):
        """
        Prepare the installation of the package

        @return: returns the latest package name or None
        @rtype: string 
        """
        # Remove the folder on boot
        try:
            # Issue 117 begin
            if os.path.exists( "%s/Toolbox/" % Settings.getDirExec() ):
            # Issue 117 end
                shutil.rmtree( "%s/Toolbox/" % Settings.getDirExec() )
        except Exception as e:
            self.error( "pre install cleanup: %s" %str(e) )
    
        # Find the latest version to install
        pkgs = os.listdir( self.pkgsToolsPath )
        latestPkg = (0,0,0)
        latestPkgName = None
        try:
            for pkg in pkgs:
                if os.path.islink( "%s/%s" % (self.pkgsToolsPath,pkg )):
                    continue
                self.trace("Package detected: %s" % pkg)
                # Example: Probes_1.2.0_Setup.tar.gz
                ver = pkg.split("_")[1].split(".")
                digits = map( int, ver )
                if tuple(digits) > latestPkg:
                    latestPkg = tuple(digits)
                    latestPkgName = pkg
        except Exception as e:
            self.error("pre install failed: %s" % str(e) )
        
        # return the package name
        return latestPkgName

    def installPkgV2(self, pkgName):
        """
        Install the package 
        More optimized, avoid cpu pic on python process

        @type  pkgName:
        @param pkgName:
        """
        t = time.time()
        try:
            DEVNULL = open(os.devnull, 'w')
            __cmd__ = "%s xf %s/%s -C %s" % (Settings.get( 'Bin', 'tar' ), 
                                             self.pkgsToolsPath, 
                                             pkgName, 
                                             Settings.getDirExec())
            ret = subprocess.call(__cmd__, shell=True, stdout=DEVNULL, stderr=DEVNULL)  
            if ret: raise Exception("unable to untar toolbox pkg")
        except Exception as e:
            self.error("toolbox installation failed: %s" % str(e) )
        self.trace("uncompress toolbox in %s sec." % (time.time()-t) )
        
    def disconnectRunningTools(self):
        """
        """
        for k1, c1 in ASI.instance().agentsRegistered.items():
            ASI.instance().stopClient(client=c1['address'] )
            
        for k2, c2 in PSI.instance().probesRegistered.items():
            PSI.instance().stopClient(client=c2['address'] )
        return True
        
    def stopDefault(self):
        """
        Stop all default probes 

        @return: 
        @rtype: 
        """
        stopped = True
        self.trace("Stop all default tools" )
        if PSI.instance() is None:
            self.trace("psi not  ready then nothing todo" )
            return None
        if self.TOOLS_INSTALLED:
            if not Settings.getInt('Boot','start-probes'):
                self.trace("The auto start option is disabled then there are no default probes started" )
                stopped = None
            else:
                self.info("Stopping default tools")
                for p in ProbesManager.instance().getDefaultProbes():
                    if bool(eval(p['enable'])):
                        ret = ProbesManager.instance().stopProbe( pname=p['name'] )
                        if not ret: stopped = False
                for a in AgentsManager.instance().getDefaultProbes():
                    if bool(eval(a['enable'])):
                        ret = AgentsManager.instance().stopAgent( aname=a['name'] )
                        if not ret: stopped = False
        else:
            stopped = None
        return stopped

    def startDefault(self):
        """
        Start all default probes

        @return: 
        @rtype: 
        """
        started = True
        self.trace("start default tools" )
        if self.TOOLS_INSTALLED :
            if not Settings.getInt('Boot','start-local-tools'):
                self.trace("auto start disabled" )
                started = None
            else:
                self.info("Starting default local tools")
                for p in ProbesManager.instance().getDefaultProbes():
                    if bool(eval(p['enable'])):
                        ret = ProbesManager.instance().startProbe( ptype=p['type'], pname=p['name'], 
                                                                   pdescr=p['description'], pdefault=True)
                        if ret != 0: started = False

                for a in AgentsManager.instance().getDefaultAgents():
                    if bool(eval(a['enable'])):
                        ret = AgentsManager.instance().startAgent( atype=a['type'], aname=a['name'], 
                                                                    adescr=a['description'], adefault=True)
                        if ret != 0: started = False
        else:
            started = None
        return started

    def getRn(self, b64=False):
        """
        Returns the release notes probes

        @return: 
        @rtype: 
        """
        self.trace("read tools rn" )
        if not self.TOOLS_INSTALLED:
            return ''
        else:
            return Context.instance().getRn( pathRn="%s/%s/" % ( Settings.getDirExec(),
                                                                Settings.get( 'Paths', 'tools' ) ) )

    def trace(self, txt):
        """
        Trace message
        """
        Logger.ClassLogger.trace(self, txt="TLM - %s" % txt)

###############################
PM = None
def instance ():
    """
    Returns the singleton

    @return: One instance of the class Context
    @rtype: Context
    """
    return PM

def initialize ():
    """
    Instance creation
    """
    global PM
    PM = ToolboxManager()

def finalize():
    """
    Destruction of the singleton
    """
    global PM
    if PM:
        PM = None

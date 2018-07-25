#! /usr/bin/env python
"""Library with keywords to handle simulation processes for JCP and JGP variants
"""

__author__ = 'Javier Ochoa (uidj5418)'
__version__ = 'See MKS'
__name__ = 'simulation'

# ================
# Trace Keywords
# ================

__all__ = [

    # --------------------
    # Simulation keywords
    # --------------------
    'start_simulation_process',
    'stop_simulation_process',
    'stop_all_simulation_processes'
]

#=================================
# Import BuildIn Python Libraries
#=================================
import sys
import os
import subprocess

#======================
# Utilities libraries
#======================

# make a reference to path: ../../resources as a module to import libraries
path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
# insert path: "../../resources" (if not previously added)
if path not in sys.path:
    sys.path.insert(0, path)

from resources.keywords.logging_lib import RobotLoggerClass

# ========================================================================================
# ==                                                                                    ==
# ==                             GLOBAL SIMULATION CLASSES                              ==
# ==                                                                                    ==
# ========================================================================================

# ======================================================
# [CLASS] ProcessManager - Global Process Manager Class
# ======================================================
class ProcessManager:
    """Class which works as a handler for simulation processes
    """

    class Process(object):
        """Class for simulation process abstraction
        """

        # file extension for stdout argument for process execution
        _STD_FILE_EXT = '.log'

        def __init__(self, filename, id, workingDirectory=None):
            """Process class constructor
            """
            self._filename = filename
            self._id = id
            self._name = None
            self._workingDirectory = workingDirectory
            self._stdFile = None
            self._processHandler = None
            # validate if filename exists
            self.__validateFileName()
            # set the current working directory as default
            if self._workingDirectory is None:
                self._workingDirectory = os.getcwd()
                SimuLogger.warning(
                    "No working directory configured for process: \"{name}\" "
                    "Current working directory will be used: \"{cwd}\"".format(
                        name=self.getName(),
                        cwd=self.getWorkingDirectory()
                    ))
            else:
                # validate if the working directory exists
                self.__validateWorkingDirectory()
            # configure and create std files for output streaming
            self.__configureStdFile()
            SimuLogger.info("New process created: \"{file}\"".format(
                file = self.getFileName()
            ))

        def getId(self):
            """returns process id
            """
            return self._id

        def getName(self):
            """returns process name (with extension)
            """
            return self._name

        def getFileName(self):
            """returns process filename
            """
            return self._filename

        def getWorkingDirectory(self):
            """returns working directory of this process
            """
            return self._workingDirectory

        def getProcessHandler(self):
            """returns process handler object
            """
            return self._processHandler

        def getStdFile(self):
            """returns STD file handler object
            """
            return self._stdFile

        def start(self):
            """starts and executes the process
            """
            errorMsg = None
            try:
                self._processHandler = subprocess.Popen(
                    self.getFileName(),
                    cwd=self.getWorkingDirectory(),
                    stdout=self.getStdFile(),
                    stderr=self.getStdFile()
                )
                SimuLogger.info("Process \"{name}\" started: {handler}".format(
                    name = self.getName(),
                    handler = self.getProcessHandler()
                ))
            except Exception as detail:
                errorMsg = detail
                self._processHandler = None
            return errorMsg

        def stop(self):
            """stops this process execution and terminates it
            """
            self._processHandler.terminate()
            try:
                processResult = self._processHandler.wait(20)
                SimuLogger.info("Process \"{name}\" terminated with result code: {result}".format(
                    name = self.getName(),
                    result = processResult
                ))
            except subprocess.TimeoutExpired:
                self._processHandler.kill()
                SimuLogger.info("Process \"{name}\" killed".format(
                    name=self.getName()
                ))
            del self._processHandler

        def __validateFileName(self):
            """check if process filename exists
            """
            if not os.path.exists(self._filename):
                raise FileNotFoundError("File does not exists: \"{f}\"".format(f=self._filename))
            else:
                self._filename = os.path.normpath(self._filename)
                self._name = os.path.basename(self._filename)

        def __validateWorkingDirectory(self):
            """check if the working directory in which the process will run exists
            """
            if not os.path.exists(self._workingDirectory):
                raise FileNotFoundError("Working directory does not exists: \"{f}\"".format(f=self._workingDirectory))
            else:
                self._workingDirectory = os.path.normpath(self._workingDirectory)

        def __configureStdFile(self):
            """builds a filename from process name for std file purposes
            and creates a that file on the working directory
            """
            # retrieve process name for std file name
            name, ext = self.getName().split('.')
            # build std filename with .log extension
            std_filename = os.path.normpath( os.path.join(
                self.getWorkingDirectory(), (name + ProcessManager.Process._STD_FILE_EXT)))
            # create std file on working directory path
            self._stdFile = open(std_filename, 'w')

    def __init__(self):
        """Process Manager constructor
        """
        self.init = True
        self.processContainer = {}

    def getAllProcesses(self):
        """Returns a dictionary with all the current processes contained
        """
        return self.processContainer

    def startProcessFromFileName(self, filename, id, workingDirectory):
        """Starts a process from a filename; arguments are validated and
        if everything is fine, no error will be return
        """
        errorMsg = None
        process = None
        try:
            # get a process object from a filename in order to start it
            process = self._getProcessFromFileName(filename, id, workingDirectory)
            self._startProcess(process)
            # load the started process into the container
            self.processContainer[process.getId()] = process
        except Exception as detail:
            errorMsg = detail
        return process, errorMsg

    def stopProcess(self, id):
        """Stop a process by searching the ID in the container
        """
        errorMsg = None
        # check if processID exists on the container
        if id in self.processContainer.keys():
            process = self.processContainer.pop(id)
            process.stop()
        else:
            errorMsg = "No process ID with name: \"{name}\"".format(name=id)
        return errorMsg

    def stopAllProcesses(self):
        """Stop all the processes that are currently in the container
        """
        errorMsg = None
        # check if there is any process in the container
        if self.getAllProcesses():
            for process in list(self.processContainer.values()):
                process.stop()
            self.processContainer.clear()
        else:
            errorMsg = "There is no simulation process currently running to be stopped"
        return errorMsg

    def _getProcessFromFileName(self, filename, id, workingDirectory):
        """creates a new process if all arguments and returns the process object
        """
        process = None
        process = ProcessManager.Process(filename, id, workingDirectory)
        return process

    def _startProcess(self, process):
        """starts a process by calling its function
        """
        errorMsg = process.start()
        if errorMsg is not None:
            raise AssertionError("Process \"{p}\" could not be started: {error}".format(
                p = process.getName(),
                error = errorMsg
            ))

#-----------------------
# SIMU Global Instances
#-----------------------

# global instance to manage all processes execution
GlobalProcessManager = ProcessManager()

# logger instance
SimuLogger = RobotLoggerClass("Simulation")

# ===============================================
# [SIMULATION] KEYWORD: start simulation process
# ===============================================
def start_simulation_process( filename, processID, workingDirectory ):
    """
    Starts a simulation process from the filename specified with the .exe
    extension; a ProcessID has to be configured to handle this process for
    other purposes.

    Parameters:
    - [filename] - process filename (path/process.exe)
    - [processID] - string to identify the process to be executed
    - [workingDirectory] - Directory in which the process will be executed

    Returns:
    A string with the process ID

    Example:
    | ${process} = | start simulation process | path/NEC_V850_proj.exe | JCP | path |
    """
    process, errorMsg = GlobalProcessManager.startProcessFromFileName(
        filename, processID, workingDirectory)
    if errorMsg is not None:
        raise AssertionError(errorMsg)
    return process.getId()

# ==============================================
# [SIMULATION] KEYWORD: stop simulation process
# ==============================================
def stop_simulation_process( processID ):
    """
    Stops an specific simulation process by ID

    Parameters:
    - [processID] - String with the process identifier

    Returns:
    Nothing

    Example:
    | stop simulation process | basesys |
    """
    errorMsg = GlobalProcessManager.stopProcess(processID)
    if errorMsg is not None:
        raise AssertionError(errorMsg)

# ====================================================
# [SIMULATION] KEYWORD: stop_all_simulation_processes
# ====================================================
def stop_all_simulation_processes():
    """
    Stops all the current running simulation processes

    Parameters:
    - [None]

    Returns:
    Nothing

    Example:
    | stop all simulation processes |
    """
    errorMsg = GlobalProcessManager.stopAllProcesses()
    if errorMsg is not None:
        raise AssertionError(errorMsg)

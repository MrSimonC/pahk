"""
Python Auto HotKey V 1.0.0 (Unicode) by Gabriel Dube
Python Auto HotKey V 1.0.1 updated by Simon Crouch 21/Dec/15 to allow use with pyinstaller
"""

from ctypes import cdll, c_wchar_p, c_int, c_bool, pointer
# from site import getsitepackages

class Interpreter():
    '''
    Class representing an AutoHotkey interpreter.
    '''
    
    NOT_EXECUTE = 0
    UNTIL_RETURN = 1
    UNTIL_BLOCK_END = 2
    ONLY_ONE_LINE = 3
    
    def __init__(self, ignore = False):
        '''
            Args:
                ignore(bool): Ignore errors
        '''

        import sys, os
        if hasattr(sys, "frozen"):
            self.ahk_dll = cdll.LoadLibrary(os.path.dirname(sys.executable) + '/autohotkey.dll')
        else:
            from site import getsitepackages
            for dll_path in getsitepackages():
                try:
                    self.ahk_dll = cdll.LoadLibrary(dll_path + '/AutoHotkey.dll')
                except:
                    pass

        self.ahk_script = ''
        self.ahk_thread = None
        self.ignore = ignore
        
    def execute_file(self, path, option = '', param = ''):
        '''
            Args:
                path(string): Path to an ahk script file.
                option(string):Additional parameter passed to AutoHotkey.dll
                param(string):Parameters passed to dll.
            
            rtype: Int
            return: Thread handle
            
            Load an ahk script file and execute it from the interpreter.
        '''
        _execute_file = self.ahk_dll.ahkdll
        _execute_file.argtypes = [c_wchar_p, c_wchar_p, c_wchar_p]
        _execute_file.restype  = c_int
        
        self.ahk_thread =  _execute_file(path, option, param)
        self.ahk_script = '\n'+open(path,'r').read()
        
        return self.ahk_thread
        
    def execute_script(self, script, option = '', param = ''):
        '''
            Args:
                script(string): String representing an ahk script
                option(string):Additional parameter passed to AutoHotkey.dll
                param(string):Parameters passed to dll.
            
            rtype: Int 
            return: Thread handle
            
            Load an ahk script and execute it from the interpreter.
        '''
        
        _execute_script = self.ahk_dll.ahktextdll        
        _execute_script.argtypes = [c_wchar_p, c_wchar_p, c_wchar_p]
        _execute_script.restype  = c_int
        
        self.ahk_thread = self, _execute_script(script, option, param)
        self.ahk_script = '\n'+script
        
        return self.ahk_thread
        
    def ready(self):
        '''
            rType: Bool
            return: "True" if a script is running, "False" otherwise.
           
            Used to check if a thread is running or not on the interpreter.
        '''
       
        ahk_ready = self.ahk_dll.ahkReady
        ahk_ready.restype = c_bool
       
        return ahk_ready()
        
    
    def terminate(self):
        '''
            Terminate the running thread.
        '''
        
        ahk_terminate = self.ahk_dll.ahkTerminate
        ahk_terminate.restype = c_int
        
        if self.ahk_thread == None and self.ignore == False:
            raise RuntimeError
        else:
            return ahk_terminate()
        
    def reload(self):
        '''
            Used to terminate and start a running script again.
        '''
        
        ahk_reload = self.ahk_dll.ahkReload
        ahk_reload.restype = c_int
        
        if self.ahk_thread == None and self.ignore == False:
            raise RuntimeError
        else:
            return ahk_reload()
            
    def pause(self, paused):
        '''
            Args:
                paused(bool): Wether the interpreter will be paused or not.
        
            rType: int
            return: 1 if paused, 0 if not
            
            ahkPause will pause/un-pause a thread and run traditional AutoHotkey Sleep internally.

            The thread remains active and you can still do various things with it like getvar.
        '''
        
        ahk_pause = self.ahk_dll.ahkPause
        ahk_pause.argtypes = [c_bool]
        ahk_pause.restype = c_int        
        
        if self.ahk_thread == None and self.ignore == False:
            raise RuntimeError
        else:
            return ahk_pause(paused)
            
    def add_file(self, path, allow_duplicate_include = False, 
                          ignore_load_failure = False):
                              
        '''
            Args:
                path(str): Path the the script file to add.
                allow_duplicate_include(bool): Allow duplicate includes.
                ignore_load_failure(bool): Ignore if loading a file failed.
            
            rType: int
            return: A pointer to the first line of new created code.            
            
            Includes additional script from a file to the running script
        '''
        
        ahk_add_file = self.ahk_dll.addFile
        ahk_add_file.argtypes = [c_wchar_p, c_bool, c_bool]
        ahk_add_file.restype = c_int
        
        lp_l = ahk_add_file(path, allow_duplicate_include, ignore_load_failure)
        
        if lp_l != -1:
            self.ahk_script +='\n' + open(path,'r').read()
    
            return lp_l
        
        elif lp_l == -1 and self.ignore == False:
            raise RuntimeError
            
        else:
            return None
            
    def add_script(self, script, execute = False):
        
        '''
        Args:
                script(str): Script to add.
                execute(bool): Determines whether the added script should be executed.
            
            rType: int
            return: A pointer to the first line of new created code.            
            
            Includes additional script from a file to the running script
        '''
        
        ahk_add_file = self.ahk_dll.addScript
        ahk_add_file.argtypes = [c_wchar_p, c_bool]
        ahk_add_file.restype = c_int
        
        lp_l = ahk_add_file(script, execute)
        
        if lp_l != -1:
            self.ahk_script += '\n'+script
            return lp_l
        elif lp_l == -1 and self.ignore == False:
            raise RuntimeError
            
        else:
            return None
        
        
    def quick_exec(self, script):
        '''
            Args:
                script(string): Ahk script to execute
                
            rType: Bool
            return: Returns True if script was executed and False if there was an error.
            
            Execute the code and delete it before it returns. Do not replace the current interpreter script
        '''
        exec_ = self.ahk_dll.ahkExec
        exec_.argtypes = [c_wchar_p]
        exec_.restype = c_int
        
        return exec_(script)
        
    def exec_line(self, lp_line, mode = 1, wait = False):
        '''
            Args:
                lp_line(pointer) : A pointer to the line where execution will start.
                mode(int): Which execution mode to use.
                waint(bool): Wait for execution to finish.
                
            rType: int
            return: If no lp_line is passed it returns a pointer to FirstLine, else it returns a pointer to NextLine.
                
            exec_line is used to execute the script from previously added line via addScript or addFile.
        '''
        
        ahk_exec_line = self.ahk_dll.ahkExecuteLine
        ahk_exec_line.argtypes = [c_int, c_int, c_bool]
        ahk_exec_line.restype = c_int
        
        lp_l = ahk_exec_line(lp_line, mode, wait)
        
        if lp_l != -1:
            return pointer(c_int(lp_l))
        
        elif lp_l == -1 and self.ignore == False:
            raise RuntimeError
            
        else:
            return None
            
    def exec_label(self, name, nowait = False):
        '''
            Args:
                name(str): Name of the label to execute
                nowait(bool): Do not to wait until execution finished.  0 - GoSub (default) 1 - GoTo (PostMessage mode)
                
            rType: int
            return: 1 if label exists 0 otherwise.
            
            Used to launch a Goto/GoSub routine in script.
        '''
        
        ahk_exec_label = self.ahk_dll.ahkLabel
        ahk_exec_label.argtypes = [c_wchar_p, c_bool]
        ahk_exec_label.restype = c_int
        
        return ahk_exec_label(name, nowait)
        
            
    def var_assign(self, name, value, create = True):
        '''
            Args:
                name(str): Variable name
                value(str): Variable value
                create(bool): Wether to create a variable if not found
                
            rType: int
            return: Returns value is 0 on success and -1 on failure.
            
            Used to assign a string to a variable in script.
        '''
        
        ahk_var_assign = self.ahk_dll.ahkassign
        ahk_var_assign.argtypes = [c_wchar_p, c_wchar_p]
        ahk_var_assign.restype = c_int
        
        if create:
            return ahk_var_assign(name, value)
        else:
            if self.var_get(name) != '':
                return ahk_var_assign(name, value)
                
    def vars_assign(self, var_dict, create = True):
        '''
            Args:
                var_dict(dict): Dictionnary containing varaibles and values to add ie:{'VarName':'VarValue'}
                create(bool): Wether to create variables if not found
                
            rType: int
            return: Always return 0
            
            Used to assign a string to a variable in script.
        '''
        
        if create:
            for name, value in var_dict.items():
                self.var_assign(name, value)
        
        else:
            for name, value in var_dict.items():
                if self.var_get(name) != '':
                    self.var_assign(name, value)
        
        return 0
            
    def var_get(self, name, get_pointer = False):
        '''
            Args:
                name(str): Variable name
                get_pointer(bool): Get value or pointer.
                
            rType: string
            return: A string representing a value or a pointer. Return empty an
            empty string if the variable is not found.
            
            Used to get a value from a variable in script
        '''
        
        ahk_var_get = self.ahk_dll.ahkgetvar
        ahk_var_get.argtypes = [c_wchar_p, c_bool]
        ahk_var_get.restype = c_wchar_p
        
        return ahk_var_get(name, get_pointer)
        
    def vars_get(self, var_list, get_pointer = False):
        '''
            Args:
                var_list(List): List of variable names.
                get_pointer(bool): Get value or pointer.
                
            rType: dict
            return: A dictionnary containing {'VarName':'VarValue'}
            
            Used to get a value from a variable in script
        '''
        var_dict = {}
        
        for i in var_list:
            var_dict[i] = self.var_get(i, get_pointer)
            
        return var_dict
    
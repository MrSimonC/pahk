# PAHK
This module combines [Python](http://Python.org) and [AutoHotKey](https://autohotkey.com/), originally written by Gabriel Dube (whom I've never met, but am exceptionally grateful to for writing this), hosted on [Google code archive](https://code.google.com/p/pahk/). See this archive page for full details on pahk.

## Install
Extract the zip files, the use `python setup.py install` to install, or manually put pahk.py, AutoHotkey.dll in Python/Lib/site-packages.

The zip files are the original hosted on [Google code archive](https://code.google.com/p/pahk/), but the pahk.py file I've edited to allow it to be used when freezing code with [pyinstaller](http://www.pyinstaller.org/). Simply include AutoHotKey.dll in your .exe directory after freezing.

## Usage
```python
import pahk
ahk_code = 'MsgBox Hello World!'
ahk_interpreter = pahk.Interpreter()
ahk_interpreter.execute_script(ahk_code)
```

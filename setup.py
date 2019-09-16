import sys
from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need fine tuning.
#build_exe_options = {"packages": ["os"], "excludes": ["tkinter"]}

# GUI applications require a different base on Windows (the default is for a
# console application).
#if sys.platform == "win32":
#    base = "Win32GUI"

setup(  name = "Outside Alone",
        version = "0.1",
        description = "Zombie survival game",
        options = {"build_exe": {"include_files": "Game/"}},
        executables = [Executable("Outside Alone.pyw")])

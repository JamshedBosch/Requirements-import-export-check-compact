import os
import sys

def get_exe_directory():
    """Get the executable or script directory"""
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__)) 
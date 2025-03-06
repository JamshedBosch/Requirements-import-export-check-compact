# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.win32.versioninfo import VSVersionInfo, FixedFileInfo, StringFileInfo, StringTable, StringStruct, VarFileInfo, VarStruct
import os
import re

# Read version from version.py
with open('version.py', 'r') as f:
    version_content = f.read()
    version_match = re.search(r"__version__\s*=\s*['\"]([^'\"]+)['\"]", version_content)
    company_match = re.search(r"__company__\s*=\s*['\"]([^'\"]+)['\"]", version_content)
    product_match = re.search(r"__product_name__\s*=\s*['\"]([^'\"]+)['\"]", version_content)
    
    VERSION = version_match.group(1) if version_match else '4.0.0'
    COMPANY = company_match.group(1) if company_match else 'Robert Bosch GmbH'
    PRODUCT_NAME = product_match.group(1) if product_match else 'Requirements Import Export Checker'

# Convert version string to tuple (e.g., '4.0.0' -> (4, 0, 0, 0))
version_tuple = tuple(map(int, VERSION.split('.'))) + (0,)

block_cipher = None

# Version information for the executable
version_info = VSVersionInfo(
    ffi=FixedFileInfo(
        filevers=version_tuple,
        prodvers=version_tuple,
        mask=0x3f,
        flags=0x0,
        OS=0x40004,
        fileType=0x1,
        subtype=0x0,
        date=(0, 0)
    ),
    kids=[
        StringFileInfo([StringTable('040904B0', [
            StringStruct('CompanyName', COMPANY),
            StringStruct('FileDescription', PRODUCT_NAME),
            StringStruct('FileVersion', VERSION),
            StringStruct('InternalName', 'ImportExportChecker'),
            StringStruct('OriginalFilename', 'ImportExportChecker.exe'),
            StringStruct('ProductName', PRODUCT_NAME),
            StringStruct('ProductVersion', VERSION)])]),
        VarFileInfo([VarStruct('Translation', [1033, 1200])])
    ]
)

# Create runtime hook file that runs before any imports
with open('pre_import_hook.py', 'w') as f:
    f.write("""
import os
import sys

# Disable color output
os.environ["COLORCLASS_DISABLE"] = "1"
os.environ["NO_COLOR"] = "1"

# Create dummy sys.stderr if needed
if sys.stderr is None:
    class DummyStderr:
        def flush(self): pass
        def write(self, *args, **kwargs): pass
    sys.stderr = DummyStderr()

# Create dummy colorclass module
class DummyColorClass:
    def __init__(self, *args, **kwargs):
        self.text = args[0] if args else ""
    def __str__(self):
        return self.text

class Windows:
    @staticmethod
    def enable(*args, **kwargs):  # Accept any arguments but do nothing
        pass
    @staticmethod
    def disable(*args, **kwargs):  # Accept any arguments but do nothing
        pass

class ColorClass:
    def __init__(self, *args, **kwargs):
        pass
    def __call__(self, *args, **kwargs):
        return args[0] if args else ""

# Create and inject the dummy colorclass module
colorclass_module = type('colorclass', (), {
    'Color': DummyColorClass,
    'Windows': Windows,
    'ColorClass': ColorClass,
    '__version__': '0.0.0',
    'is_windows': True,
    'is_linux': False,
    'is_mac': False
})

sys.modules['colorclass'] = colorclass_module
""")

a = Analysis(
    ['ImportExportChecksGUI.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('icons', 'icons'),  # Icon files for the application
        # Add any additional data files here
    ],
    hiddenimports=[
        'oletools.thirdparty.tablestream.tablestream',
        'pyreqif.xlsx',
        'pyreqif.extractOleData',
        'oletools.rtfobj',
        'colorclass',  # Include colorclass for colored output
        # Qt-related imports
        'PyQt6.QtCore',
        'PyQt6.QtGui',
        'PyQt6.QtWidgets'
    ],
    hookspath=['.'],
    hooksconfig={},
    runtime_hooks=['pre_import_hook.py'],
    excludes=[
        'PyQt5',    # Exclude PyQt5 to prevent conflicts
        'PySide6',  # Exclude PySide6 to prevent conflicts
        'PySide2'   # Exclude PySide2 to prevent conflicts
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='ImportExportChecker',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Set to True if you need console output for debugging
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    version=version_info,  # Add version information
    # icon='path/to/icon.ico',  # Uncomment and set path to add an application icon
)

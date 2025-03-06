# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

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
    datas=[('icons', 'icons')],
    hiddenimports=[
        'oletools.thirdparty.tablestream.tablestream',
        'pyreqif.xlsx',
        'pyreqif.extractOleData',
        'oletools.rtfobj',
        'colorclass'  # Include colorclass
    ],
    hookspath=['.'],
    hooksconfig={},
    runtime_hooks=['pre_import_hook.py'],  # Use our pre-import hook
    excludes=[],  # Don't exclude colorclass
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
    console=False,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

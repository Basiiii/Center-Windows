from distutils.core import setup
import py2exe

setup(windows=[{
    'script': 'Center-Windows.py',
    'icon_resources': [(1, 'icon.ico')]
  }],
  options={
    "py2exe": {
        "optimize": 2,
    }
  },
  data_files=[('.', ['icon.ico'])]
)

from setuptools import setup

setup(name='easyanimation',
      version='0.1',
      description='Wrapper for live plotting in matplotlib and Qt',
      author='Adrian Garcia Badaracco',
      author_email='adrian@adriangb.com',
      url='https://github.com/adriangb/easyanimation',
      package_dir={'easyanimation': 'src'},
      packages=['easyanimation'],
      install_requires=['numpy>=1.16', 'matplotlib>=3.1', 'pyside2>5.12',
                        'pyqtgraph@git+ssh://git@github.com/pyqtgraph/pyqtgraph@develop#egg=pyqtgraph'],
      python_requires='>=3.7',
      )

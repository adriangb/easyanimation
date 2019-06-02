from setuptools import setup, find_packages

setup(name='EasyAnimation',
      version='1.0',
      description='Wrapper for live plotting in matplotlib and Qt',
      author='Adrian Garcia Badaracco',
      author_email='adrian@adriangb.com',
      url='https://github.com/adriangb/easy_animation',
      packages=find_packages(),
      scripts=['test_animation.py'],
      install_requires=['numpy>=1.16.4', 'matplotlib>=3.1.0', 'pyqtgraph git+ssh://git@github.com/pyqtgraph/pyqtgraph@master#egg=pyqtgraph'],
      python_requires='>=3.6',
      )

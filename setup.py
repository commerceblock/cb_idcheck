# Copyright (c) 2018 The CommerceBlock Developers                                                                                                              
# Distributed under the MIT software license, see the accompanying                                                                                             # file LICENSE or http://www.opensource.org/licenses/mit-license.php.  

from setuptools import setup, find_packages
def readme():
    with open('README.md') as f:
        return f.read()

setup(name='cb_idcheck',
      version='0.1',
      description='CommerceBlock KYC utilities',
      classifiers=[
        'Programming Language :: Python :: 3.6'
      ],
      url='http://github.com/commerceblock/cb_idcheck',
      author='CommerceBlock',
      author_email='lawrence.deacon@gmail.com',
      license='MIT',
      packages=['cb_idcheck'],
      install_requires=['onfido', 'python-magic', 'flask', 'simplejson', 'numpy', 'pymongo'])

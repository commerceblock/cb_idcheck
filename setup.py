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
      packages=['cb_idcheck', 'cb_idcheck.test_framework'],
      install_requires=['onfido', 'python-magic', 'flask', 'simplejson', 'numpy', 'pymongo'])

from setuptools import setup
def readme():
    with open('README.rst') as f:
        return f.read()

setup(name=cb_idcheck,
      version='0.1',
      description='CommerceBlock KYC utilities',
      classifiers=[
        'Programming Language :: Python :: 3.6'
      ]
      url='http://github.com/commerceblock/cb_idcheck',
      author='Lawrence Deacon',
      author_email='lawrence.deacon@gmail.com',
      license='MIT',
      packages=['cb_idcheck'],
      install_requires=['onfido', 'python-magic', 'flask', 'simplejson']
      zip_safe=False)

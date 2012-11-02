from setuptools import setup
import os
import re

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

__version__ = re.search( "__version__\s*=\s*'(.*)'", read('spiro/__init__.py'), re.M).group(1)
assert __version__

long_description = read("README.md")
assert long_description

setup(
    name = "spiro",
    version = __version__,
    description = "A python spider using Tornado",
    long_description = long_description,
    author = "David Koblas",
    author_email = "david@koblas.com",
    url = "",
    license = "BSD",
    packages = ['spiro'],
    include_package_data = True,
    install_requires = [
        # 'pyzmq>=2.0.10',
        'tornado>=2.2',
        'brownie>=0.4.1',
    ],
    # test_suite = 'nose.collector',
    # tests_require = tests_require,
    # extras_require = {'test': tests_require},
    entry_points = {
        'console_scripts' : [
            'spiro = spiro.app',
        ]
    },
    classifiers = [
        'Intended Audience :: Developers',
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Information Technology',
        'License :: OSI Approved :: BSD License',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Indexing/Search',
    ]
)

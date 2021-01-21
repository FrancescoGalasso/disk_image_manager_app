# coding: utf-8

# pylint: disable=missing-docstring
# pylint: disable=invalid-name

import os
import subprocess

from setuptools import setup, find_packages

about = {}
here = os.path.abspath(os.path.dirname(__file__))
with open(file=os.path.join(here, 'dima', '__version__.py'), mode='r', encoding='utf-8') as f:
    exec(f.read(), about)   # pylint: disable=exec-used

with open(file='README.md', mode='r', encoding='utf-8') as f:
    readme = f.read()

requires = []


def _verify_platform():
    cmd = ['uname', '-m']
    output = subprocess.check_output(cmd, shell=True).decode("utf-8")
    if output == 'x86_64':
        requires.append('PyQt5 == 5.15.2')
    elif output == 'armv7l':  # raspian buster
        pass


def main():

    _verify_platform()

    setup(
        name=about['__title__'],
        version=about['__version__'],
        description=about['__description__'],
        long_description=readme,
        long_description_content_type='text/markdown',
        author=about['__author__'],
        author_email=about['__author_email__'],
        python_requires=">=3.6",
        license=about['__license__'],
        zip_safe=False,
        classifiers=[
            'Development Status :: 3 - Alpha',
            'Natural Language :: English',
            'License :: OSI Approved :: MIT License',
            'Operating System :: POSIX :: Linux',
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: 3.6',
            'Programming Language :: Python :: 3.7',
            'Programming Language :: Python :: 3.8',
            'Programming Language :: Python :: 3.9',
        ],
        packages=find_packages(),
        data_files=[],
        scripts=[],
        install_requires=requires,
    )


if __name__ == '__main__':
    main()

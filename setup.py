# coding: utf-8

# pylint: disable=missing-docstring
# pylint: disable=invalid-name

import os
import glob

from setuptools import setup, find_packages

about = {}
here = os.path.abspath(os.path.dirname(__file__))
with open(file=os.path.join(here, 'dima', '__version__.py'),  mode='r', encoding='utf-8') as f:
    exec(f.read(), about)

with open(file='README.md', mode='r', encoding='utf-8') as f:
    readme = f.read()


__app_name__ = 'alfa_CR6'


def main():
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
        # package_dir={'': 'dima'},
        data_files=[
            # ('alfa_CR6_ui/ui', list(glob.glob('src/alfa_CR6_ui/ui/*.ui'))),
            # ('alfa_CR6_ui/keyboard', list(glob.glob('src/alfa_CR6_ui/keyboard/*.json'))),
            # ('alfa_CR6_ui/images', list(glob.glob('src/alfa_CR6_ui/images/*'))),
            # ('alfa_CR6_test/fixtures', list(glob.glob('src/alfa_CR6_test/fixtures/*'))),
        ],
        # include_package_data=True,
        scripts=[
            # 'bin/alfa_CR6',
            # 'bin/alfa_CR6_test',
        ],
        install_requires=[
            'PyQt5 == 5.15.2',
            # 'websockets',
            # 'SQLAlchemy',
            # 'jsonschema',
            # 'python-barcode',
            # 'Pillow',
            # 'aiohttp',
        ],
    )


if __name__ == '__main__':
    main()

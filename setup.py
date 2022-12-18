from setuptools import setup, find_packages
import codecs

with codecs.open('README.md', encoding='utf-8') as file:
    long_description = file.read()

setup(
    name='uniarchive',
    version='0.1.0',
    author='Artur Misyunas',
    description='Moves all files from all members of a group to an archive folder',
    long_description=long_description,
    scripts=[
        'uniarchivator/uniarchivator.py',
    ],
    packages=find_packages(),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Natural Language :: English',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Utilities',
    ],
)

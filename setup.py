from setuptools import setup, find_packages
import codecs

with codecs.open('README.md', encoding='utf-8') as file:
    long_description = file.read()

setup(
    name='uniarchivator',
    version='0.1.0',
    author='Artur Misyunas',
    description='Moves all files from all members of a group to an archive folder',
    long_description=long_description,
    url='https://github.com/kotbegimot/uniarchive.git',
    packages=find_packages(include=['uniarchivator', 'uniarchivator.*']),
    setup_requires=['pytest-runner'],
    tests_require=['pytest'],
    entry_points={
        'console_scripts': ['uniarchivator=uniarchivator.uniarchivator:main']
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Natural Language :: English',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Utilities',
    ],
)

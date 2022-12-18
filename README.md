# Uniarchivator

Moves all files from all members of a group to an archive. 
Receives as parameters the name of the group, the path for the group files searc and the name of the resulting archive.
The script writes logs to the console and the file `/tmp/uniarchivator_journal.log`.

The script supports multiple launches at the same time.
The script is installable as a Debian package.

## Prerequisites
Before you continue, ensure you have met the following requirements:
- You have installed the `Python3` and `pip3` packages

## Install
 - Download project from github:

```git clone https://github.com/kotbegimot/uniarchive.git```
 - Move to the directory which contains `setup.py` file
 - To install python package run:

```pip install -e . OR python3 setup.py install```

 - To build `deb` package:

```python3 setup.py --command-packages=stdeb.command bdist_deb```

## Usage
```uniarchivator.py test_group```

Moves all files from all members of a test_group that were found by default path /home group to the archive file test_group.zip. 

```uniarchivator --path /usr --name test_file another_group```

Moves all files from all members of a another_group that were found by path /usr group to the archive file test_file.zip. 


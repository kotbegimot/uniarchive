#!/usr/bin/python3

import argparse
import sys
import textwrap
import grp
import os
import errno
from pathlib import Path
import subprocess
from enum import Enum
import time
import shutil
from concurrent.futures import ProcessPoolExecutor
import multiprocessing as mp
from pwd import getpwuid
import logging

class Errors(Enum):
    """
    Script error codes
    """
    ERR_GROUP_NOT_FOUND = 1
    ERR_ARCH_FILE_EXIST = 2
    ERR_DEFAULT_PATH = 3
    ERR_FIND_FILES = 4
    ERR_NO_FILES = 5
    ERR_GROUP_RESTRICTED = 6
    ERR_USER_RESTRICTED = 7
    ERR_SOURCE_DIR_INVALID = 8
    ERR_RUN_FIND = 9
    ERR_FIND_GROUP_MEMBERS = 10
    ERR_COLLISION_GROUP = 11
    ERR_COLLISION_USERS = 12
    ERR_ARCHIVATION_ERROR = 13

# default acrchive file extension
ARCH_FILE_EXTENSION = ".tgz"
# default acrchive file path
DEFAULT_ARCH_FILE_PATH = "/tmp/group_archives"
ARCHIVE_EXTENSION = 'zip'
# default starting point for group files searching
DEFAULT_SOURCE_PATH = "/home"
# Number of processes to create mp.cpu_count()
WORKERS = mp.cpu_count()
# restrictions
RESTRICTED_GROUPS = ["root"]
RESTRICTED_USERS = ["root"]

"""
Configures app logger
"""
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
# Create handlersx
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
file_handler = logging.FileHandler('/tmp/uniarchive_journal.log')
# Create formatters and add it to handlers
console_format = logging.Formatter('[%(levelname)s] - %(message)s')
file_format = logging.Formatter('%(asctime)s : [%(levelname)s] - %(message)s')
console_handler.setFormatter(console_format)
file_handler.setFormatter(file_format)
# Add handlers to the logger
logger.addHandler(console_handler)
logger.addHandler(file_handler)

def check_target_path(folder_path):
    """
    Checks default folder existance and creates it if needed.

    Args:
        user_group: linux user's group from input argument

    Returns:
        None
    """
    try:
        os.makedirs(folder_path)
    except OSError as err:
        if err.errno != errno.EEXIST:
            logger.error(f'Failed to create path {folder_path}: {err}')
            sys.exit(Errors.ERR_DEFAULT_PATH)
    else:
        logger.info(f"Path has been created: {folder_path}")

def delete_files(dir_path):
    """
    Deletes directory with an archive source files

    Args:
        file_path: deketing directory path
    Returns:
        None
    """
    try:
        shutil.rmtree(dir_path)
    except OSError as e:
        print("Error: %s : %s" % (dir_path, e.strerror))


def move_files(src_path_list, dest_folder_path):
    """
    Moves a list of files to a target directory

    Args:
        src_path_list: list of full paths of source files
        dest_folder_path: target folder path

    Returns:
        None
    """
    for src_path in src_path_list:
        file_owner = getpwuid(os.stat(src_path).st_uid).pw_name
        dest_path = f"{dest_folder_path}/{file_owner}/{os.path.basename(src_path)}"
        try:
            shutil.move(src_path, dest_path)
            logger.debug(f'moved {src_path} to {dest_path}')
        except FileNotFoundError:
            logger.error(f'File {src_path} not found')
        except Exception as err:
            logger.error(f'File {src_path} copy failed: {err}')

def check_source_path(src_path):
    """
    Checks existance of starting point for group files searching

    Args:
        src_path: starting point for group files searching

    Returns:
        None
    """
    if not os.path.isdir(src_path):
        logger.error(f"Path {src_path} does not exist!")
        sys.exit(Errors.ERR_SOURCE_DIR_INVALID)

def check_group(group_name):
    """
    Checks the users group existance

    Args:
        group_name: list of full paths of source files

    Returns:
        None
    """
    try:
        grp.getgrnam(group_name)
    except KeyError:
        logger.error(f"Group {group_name} does not exist!")
        sys.exit(Errors.ERR_GROUP_NOT_FOUND)

    if group_name in RESTRICTED_GROUPS:
        logger.error(f"Group {group_name} is restricted!")
        sys.exit(Errors.ERR_GROUP_RESTRICTED)

def check_output_file(arch_file):
    """
    Checks the archive file existance

    Args:
        arch_file: Path to the archive file

    Returns:
        None
    """
    if os.path.isfile(arch_file):
        logger.error(f"Archive file {arch_file} already exists!")
        sys.exit(Errors.ERR_ARCH_FILE_EXIST)

def check_restrictions_and_collisions(group_name):
    """
    Validates the group members for collisions and restrictions 

    Args:
        group_name: Group name

    Returns:
        None
    """
    members_names_list = []
    processing_groups = []
    processing_members = set()
    # check group members restrictions
    members_names_list = grp.getgrnam(group_name).gr_mem
    if any(item in members_names_list for item in RESTRICTED_USERS):
        print('Group {group_name} has restricted user: {RESTRICTED_USERS}')
        sys.exit(Errors.ERR_USER_RESTRICTED)
    # check group collisions
    processing_groups = next(os.walk(f'{DEFAULT_ARCH_FILE_PATH}'))[1]
    if processing_groups:
        if group_name in processing_groups:
            logger.error(f'Other process with group {group_name} is running. Affected groups: {processing_groups}')
            sys.exit(Errors.ERR_COLLISION_GROUP)
        for proc_grp in processing_groups:
            processing_members.update(grp.getgrnam(proc_grp).gr_mem)
        logger.error(f'processing_members: {processing_members}')
        if any(item in members_names_list for item in processing_members):
            logger.error(f'Other process with some of group {group_name} members {members_names_list} is running. Affected groups: {processing_members}')
            sys.exit(Errors.ERR_COLLISION_USERS)

def create_folders(group_name):
    """
    Create folders for group users

    Args:
        group_name: Group name

    Returns:
        None
    """
    members_list = grp.getgrnam(group_name).gr_mem
    # check default path
    check_target_path(f"{DEFAULT_ARCH_FILE_PATH}/{group_name}")
    # create folders for group users
    for member in members_list:
        check_target_path(f"{DEFAULT_ARCH_FILE_PATH}/{group_name}/{member}")


if __name__ == "__main__":
    if '--help' in sys.argv or '-h' in sys.argv:
        print(__doc__)

    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=textwrap.dedent('''\
        Moves all files from all members of a group to an archive folder

        EXAMPLES:

            group_archivator.py local --name local_files.tgz
        '''))
    parser.add_argument('group', type=str, help='Linux user group')
    parser.add_argument('--name', type=str, help='Name of the archive file w/o extension')
    parser.add_argument('--path', type=str, help='Source folder path')

    args = parser.parse_args()
    group = args.group
    source_path = args.path
    if args.name:
        arch_name = args.name
    else:
        arch_name = group
    if not source_path:
        source_path = DEFAULT_SOURCE_PATH

    # check source path
    check_source_path(source_path)

    # group name validation
    check_group(group)

    # Check group members
    check_restrictions_and_collisions(group)

    # Create folders
    create_folders(group)

    # check the archive file existance
    check_output_file(Path(f"{DEFAULT_ARCH_FILE_PATH}{arch_name}{ARCH_FILE_EXTENSION}"))

    # find all the files files owned by the group users
    logger.info("Files searching ...")
    start = time.perf_counter()
    files_list = []

    try:
        output = subprocess.getoutput(f"sudo find {source_path} -group {group} -type f 2>/dev/null")
    except subprocess.CalledProcessError as e:
        logger.error(f'Attempt to find user\'s group files failed: {e}')
        sys.exit(Errors.ERR_RUN_FIND)
    else:
        files_list = output.split()
        # logger.debug(f'Found files: {files_list}')

    if len(files_list) == 0:
        sys.exit(Errors.ERR_NO_FILES)

    end = time.perf_counter()
    logger.debug(f'Searching finished in {round((end-start)*1000, 1)} ms')

    # determine incrementation step
    step = round(len(files_list) / WORKERS)

    logger.info("Copying files ...")
    start = time.perf_counter()
    # move the files in several processes
    with ProcessPoolExecutor(WORKERS) as exe:
        # split the move operations into chunks
        for i in range(0, len(files_list), step):
            # select a chunk of filenames
            filefile_paths = files_list[i:(i + step)]
            # submit all file move tasks
            _ = exe.submit(move_files, filefile_paths, f"{DEFAULT_ARCH_FILE_PATH}/{group}")
    end = time.perf_counter()
    logger.debug(f'Files moving finished in {round((end-start)*1000, 1)} ms')

    # make archive
    logger.info("Making an archive ...")
    start = time.perf_counter()
    source_files_path = f"{DEFAULT_ARCH_FILE_PATH}/{group}"
    try:
        shutil.make_archive(f"{DEFAULT_ARCH_FILE_PATH}/{arch_name}", ARCHIVE_EXTENSION, source_files_path)
    except Exception as exp:
        logger.error(f'Attempt to create archive file {DEFAULT_ARCH_FILE_PATH}/{arch_name}.{ARCHIVE_EXTENSION} failed: {e}')
        sys.exit(Errors.ERR_ARCHIVATION_ERROR)
    logger.info(f"Archive file: {DEFAULT_ARCH_FILE_PATH}/{arch_name}.{ARCHIVE_EXTENSION}")
    delete_files(source_files_path)
    end = time.perf_counter()
    logger.debug(f'Archive making finished in {round((end-start)*1000, 1)} ms')

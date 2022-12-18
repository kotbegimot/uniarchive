import sys
from uniarchivator import uniarchivator
import unittest

INVALID_GROUP = "you_do_not_have_this_group"
RESTRICTED_GROUP = "root"
INVALID_PATH = "/you_do_not_have_this_path"

class TestUniarchivator(unittest.TestCase):
    def test_group_check(self):
        """
        Checks wrong users group name error: app should return Errors.ERR_GROUP_NOT_FOUND code
        """
        with self.assertRaises(SystemExit) as cm:
            uniarchivator.check_group(INVALID_GROUP)
        self.assertEqual(cm.exception.code, uniarchivator.Errors.ERR_GROUP_NOT_FOUND)
    
    def test_restricted_group(self):
        """
        Checks restricted users group name error: app should return Errors.ERR_GROUP_RESTRICTED code
        """
        with self.assertRaises(SystemExit) as cm:
            uniarchivator.check_group(RESTRICTED_GROUP)
        self.assertEqual(cm.exception.code, uniarchivator.Errors.ERR_GROUP_RESTRICTED)
        
    def check_invalid_path(self):
        """
        Checks invalid path to source files: app should return Errors.ERR_SOURCE_DIR_INVALID code
        """
        with self.assertRaises(SystemExit) as cm:
            uniarchivator.check_source_path(INVALID_PATH)
        self.assertEqual(cm.exception.code, uniarchivator.Errors.ERR_SOURCE_DIR_INVALID)    

if __name__ == '__main__':
        unittest.main()

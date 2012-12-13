#!/usr/bin/python

import unittest

from astreet import StreetTest
from h1 import H1Test
from h2 import H2Test


if __name__ == '__main__':
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(StreetTest))
    suite.addTest(unittest.makeSuite(H1Test))
    suite.addTest(unittest.makeSuite(H2Test))
    unittest.TextTestRunner(verbosity=2).run(suite)

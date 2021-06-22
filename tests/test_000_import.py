#!/usr/bin/env python

"""Tests for `datanodes` package."""


import unittest

from datanodes.core.node_window import NodeWindow
from datanodes.core.node_scene import Scene

class TestDataNodes(unittest.TestCase):
    """Tests for `datanodes` package."""

    def setUp(self):
        """Set up test fixtures, if any."""

    def tearDown(self):
        """Tear down test fixtures, if any."""

    def test_000_something(self):
        """ Test if Scene class has 'has_been_modified' attribute. """
        assert (hasattr(Scene, 'has_been_modified'))

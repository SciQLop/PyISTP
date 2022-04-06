#!/usr/bin/env python

"""Tests for `pyistp` package."""

import unittest
from ddt import ddt, data, unpack

from pyistp import ISTPLoader
import os

current_path = os.path.dirname(__file__)

test_data = (
    (f"{current_path}/resources/wi_k0_mfi_20220101_v01.cdf", [
        "PGSM", "BGSEc", "BF1", "PGSE", "N", "MODE", "BGSMa", "Time_PB5", "DIST", "BGSEa", "BGSMc", "RMS", "DQF",
        "Gap_Flag"]),
)


@ddt
class TestPyIstp(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    @data(*test_data)
    @unpack
    def test_finds_data_variables(self, fname, data_vars):
        istp_loader = ISTPLoader(file=fname)
        self.assertListEqual(data_vars, istp_loader.data_variables())

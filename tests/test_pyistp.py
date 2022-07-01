#!/usr/bin/env python

"""Tests for `pyistp` package."""

import unittest
from ddt import ddt, data, unpack

from pyistp import ISTPLoader
import os

current_path = os.path.dirname(__file__)

test_data = (
    (f"{current_path}/resources/wi_k0_mfi_20220101_v01.cdf",
     ["PGSM", "BGSEc", "BF1", "PGSE", "BGSMa", "DIST", "BGSEa", "BGSMc", "RMS"]),
    (f"{current_path}/resources/solo_l3_rpw-bia-density-10-seconds_00000000_v01.cdf",
     ["DENSITYSTD", "DENSITY"]),

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

    @data(*test_data)
    @unpack
    def test_can_load_all_data_vars(self, fname, data_vars):
        istp_loader = ISTPLoader(file=fname)
        for varname in istp_loader.data_variables():
            var = istp_loader.data_variable(var_name=varname)
            self.assertIsNotNone(var)
            self.assertGreaterEqual(len(var.axes), 1)

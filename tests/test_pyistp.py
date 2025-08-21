#!/usr/bin/env python

"""Tests for `pyistp` package."""

import unittest
from ddt import ddt, data, unpack

import pyistp
import os

current_path = os.path.dirname(__file__)

test_data = (
    (f"{current_path}/resources/wi_k0_mfi_20220101_v01.cdf",
     ["PGSM", "BGSEc", "BF1", "PGSE", "BGSMa", "DIST", "BGSEa", "BGSMc", "RMS"]),
    (f"{current_path}/resources/solo_l3_rpw-bia-density-10-seconds_00000000_v01.cdf",
     ["DENSITYSTD", "DENSITY"]),
    (f"{current_path}/resources/tha_l2_esa_00000000_v01.cdf",
     ["tha_iesa_solarwind_flag", "tha_peeb_velocity_gsm", "tha_peeb_velocity_gse", "tha_peeb_velocity_dsl",
      "tha_peeb_symm_ang", "tha_peeb_symm", "tha_peeb_ptens", "tha_peeb_t3", "tha_peeb_sc_pot", "tha_peeb_vthermal",
      "tha_peeb_avgtemp", "tha_peeb_density", "tha_peib_velocity_gsm", "tha_eesa_solarwind_flag",
      "tha_peib_velocity_gse", "tha_peib_magf", "tha_peib_symm_ang", "tha_peib_symm", "tha_peib_flux",
      "tha_peib_mftens", "tha_peib_magt3", "tha_peib_t3", "tha_peib_vthermal", "tha_peib_avgtemp", "tha_peib_density",
      "tha_peer_velocity_gsm", "tha_peer_velocity_gse", "tha_peer_magf", "tha_peer_symm_ang", "tha_peer_symm",
      "tha_peeb_fluxQ", "tha_peif_magt3", "tha_peib_en_eflux", "tha_peif_t3", "tha_peeb_velocity_gsmQ",
      "tha_peif_densityQ", "tha_peeb_sc_potQ", "tha_peeb_magf", "tha_peeb_velocity_dslQ", "tha_peeb_vthermalQ",
      "tha_peeb_avgtempQ", "tha_peif_symm", "tha_peef_symm_ang", "tha_peif_sc_pot", "tha_peib_velocity_gseQ",
      "tha_peib_velocity_dslQ", "tha_peer_magfQ", "tha_peib_magfQ", "tha_peif_en_eflux", "tha_peef_sc_potQ",
      "tha_peir_t3Q", "tha_peef_velocity_gsm", "tha_peib_mftensQ", "tha_peeb_en_efluxQ",
      "tha_peeb_t3Q", "tha_peef_ptensQ", "tha_peeb_en_eflux", "tha_peib_t3Q", "tha_peib_en_efluxQ",
      "tha_peeb_velocity_gseQ", "tha_peef_vthermal", "tha_peib_avgtempQ", "tha_peib_densityQ", "tha_peib_data_quality",
      "tha_peif_velocity_gse", "tha_peif_density", "tha_peif_symm_angQ", "tha_peer_flux", "tha_peib_vthermalQ",
      "tha_peer_avgtemp", "tha_peer_velocity_dslQ", "tha_peif_vthermal", "tha_peer_symmQ", "tha_peef_fluxQ",
      "tha_peir_mftens", "tha_peer_fluxQ", "tha_peer_mftensQ", "tha_peer_ptensQ", "tha_peef_symm", "tha_peef_t3Q",
      "tha_peeb_symm_angQ", "tha_peib_sc_potW", "tha_peer_t3Q", "tha_peib_symmQ", "tha_peir_magfQ", "tha_peef_avgtempQ",
      "tha_peif_flux", "tha_peef_magf", "tha_peef_densityQ", "tha_peif_velocity_gseQ", "tha_peef_velocity_gsmQ",
      "tha_peif_vthermalQ", "tha_peer_sc_potQ", "tha_peir_vthermal", "tha_peeb_mftensQ", "tha_peib_fluxQ",
      "tha_peir_mftensQ", "tha_peir_vthermalQ", "tha_peir_symmQ", "tha_peef_vthermalQ", "tha_peif_data_quality",
      "tha_peif_sc_potQ", "tha_peif_avgtemp", "tha_peef_mftensQ", "tha_peif_mftensQ", "tha_peir_avgtemp",
      "tha_peir_velocity_gse", "tha_peib_velocity_gsmQ", "tha_peer_vthermalQ", "tha_peir_t3", "tha_peer_mftens",
      "tha_peif_mftens", "tha_peer_velocity_gsmQ", "tha_peef_magfQ", "tha_peeb_mftens", "tha_peif_magt3Q",
      "tha_peif_velocity_gsmQ", "tha_peer_sc_pot", "tha_peif_fluxQ", "tha_peif_en_efluxQ", "tha_peir_symm_angQ",
      "tha_peeb_symmQ", "tha_peir_ptens", "tha_peir_sc_pot", "tha_peer_symm_angQ", "tha_peef_symm_angQ",
      "tha_peef_en_efluxQ", "tha_peif_ptens", "tha_peif_avgtempQ", "tha_peeb_flux", "tha_peir_ptensQ",
      "tha_peef_velocity_dslQ", "tha_peif_velocity_dslQ", "tha_peer_en_efluxQ", "tha_peir_densityQ", "tha_peer_magt3",
      "tha_peir_data_quality", "tha_peib_magt3Q", "tha_peif_ptensQ", "tha_peer_en_eflux", "tha_peer_densityQ",
      "tha_peib_ptens", "tha_peeb_magt3Q", "tha_peeb_densityQ", "tha_peib_velocity_dsl", "tha_peeb_data_quality",
      "tha_peir_avgtempQ", "tha_peib_ptensQ", "tha_peef_data_quality", "tha_peir_velocity_dslQ", "tha_peir_en_efluxQ",
      "tha_peef_en_eflux", "tha_peir_fluxQ", "tha_peir_magt3Q", "tha_peir_velocity_gsmQ", "tha_peer_data_quality",
      "tha_peer_t3", "tha_peir_density", "tha_peif_t3Q", "tha_peer_avgtempQ", "tha_peer_magt3Q", "tha_peir_sc_potQ",
      "tha_peif_magf", "tha_peir_symm", "tha_peer_velocity_gseQ", "tha_peif_velocity_dsl", "tha_peif_velocity_gsm",
      "tha_peeb_magt3", "tha_peef_density", "tha_peef_t3", "tha_peef_avgtemp", "tha_peef_sc_pot",
      "tha_peef_velocity_gse", "tha_peif_symm_ang", "tha_peef_ptens", "tha_peef_mftens", "tha_peef_flux",
      "tha_peif_symmQ", "tha_peir_flux", "tha_peib_sc_pot", "tha_peef_velocity_dsl", "tha_peir_magf",
      "tha_peef_velocity_gseQ", "tha_peef_magt3", "tha_peef_symmQ", "tha_peef_magt3Q", "tha_peif_magfQ",
      "tha_peir_en_eflux", "tha_peer_velocity_dsl", "tha_peir_magt3", "tha_peib_symm_angQ", "tha_peir_velocity_gseQ",
      "tha_peir_symm_ang", "tha_peir_velocity_dsl", "tha_peeb_ptensQ", "tha_peir_velocity_gsm", "tha_peer_density",
      "tha_peer_vthermal", "tha_peer_ptens", "tha_peeb_magfQ"]),
    (f"{current_path}/resources/thd_l2_efi_00000000_v01.cdf",
     ['thd_eff_e34_efs', 'thd_eff_q_mag', 'thd_efs_dot0_gsm', 'thd_efs_dot0_dsl', 'thd_efs_dot0_gse', 'thd_eff_q_pha',
      'thd_eff_dot0_gse', 'thd_eff_e12_efs', 'thd_eff_dot0_dsl', 'thd_eff_dot0_gsm']),
    (f"{current_path}/resources/c3_cp_efw_l3_e3d_inert_00000000_v01.cdf",
     ['delta_Ez_ISR2__C3_CP_EFW_L3_E3D_INERT', 'E_Vec_xyz_ISR2__C3_CP_EFW_L3_E3D_INERT',
      'E_sigma__C3_CP_EFW_L3_E3D_INERT']
     )
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
        istp_file = pyistp.load(file=fname)
        self.assertListEqual(sorted(data_vars), sorted(istp_file.data_variables()))

    @data(*test_data)
    @unpack
    def test_can_load_all_data_vars(self, fname, data_vars):
        istp_file = pyistp.load(file=fname)
        self.assertGreater(len(istp_file.data_variables()), 0)
        for varname in istp_file.data_variables():
            var = istp_file.data_variable(var_name=varname)
            self.assertIsNotNone(var)
            self.assertGreaterEqual(len(var.axes), 1)

    @data(*test_data)
    @unpack
    def test_can_access_global_attrs(self, fname, data_vars):
        istp_file = pyistp.load(file=fname)
        self.assertGreater(len(istp_file.attributes()), 0)
        for attrname in istp_file.attributes():
            attr = istp_file.attribute(attrname)
            self.assertIsNotNone(attr)

    def test_files_generated_by_cda_with_empty_data(self):
        istp_file = pyistp.load(file=f"{current_path}/resources/tha_l2s_fgm_CDA_NO_RECORDS.cdf")
        self.assertIsNotNone(istp_file)
        self.assertIsNone(istp_file.data_variable('tha_fge_dsl'))

    def test_non_compliant_cdf_with_master(self):
        istp_file = pyistp.load(file=f"{current_path}/resources/wi_plsp_3dp_19990329_v02.cdf",
                                master_file=f"{current_path}/resources/wi_plsp_3dp_00000000_v01.cdf")
        self.assertIsNotNone(istp_file)
        self.assertIsNotNone(istp_file.data_variable('MOM.P.AVGTEMP'))

    def test_get_data_variable_type(self):
        istp_file = pyistp.load(file=f"{current_path}/resources/solo_l3_rpw-bia-density-10-seconds_00000000_v01.cdf")
        self.assertEqual(istp_file.data_variable('DENSITY').cdf_type, 'CDF_FLOAT')

    def test_get_support_variable_type(self):
        istp_file = pyistp.load(file=f"{current_path}/resources/solo_l3_rpw-bia-density-10-seconds_00000000_v01.cdf")
        self.assertEqual(istp_file.data_variable('DENSITY').axes[0].cdf_type, 'CDF_TIME_TT2000')

    def test_is_nrv(self):
        istp_file = pyistp.load(file=f"{current_path}/resources/solo_l3_rpw-bia-density-10-seconds_00000000_v01.cdf")
        self.assertFalse(istp_file.data_variable('DENSITY').axes[0].is_nrv)

    def test_get_axis_values_from_master_as_fallback(self):
        # https://github.com/SciQLop/speasy/issues/223
        istp_file = pyistp.load(file=f"{current_path}/resources/sta_l1_het_20240103_v01.cdf",
                                master_file=f"{current_path}/resources/sta_l1_het_00000000_v01.cdf")
        self.assertIsNotNone(istp_file)
        self.assertIsNotNone(istp_file.data_variable('Proton_Flux'))

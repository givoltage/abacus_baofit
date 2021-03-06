# -*- coding: utf-8 -*-
"""
Created on Mon Dec 31 15:39:16 2018
@author: givoltage

determine the best fitting model for iterative reconstruction by using
different fitting options for two models with the same truth. only use 16 boxes

change polytype, rmin, and Hdir in baofit

"""


from baofit import baofit
import os
from contextlib import closing
from abacus_hod import MyPool
from itertools import product

sim_name_prefix = 'AbacusCosmos_1100box_planck'
tagout = ''
prod_dir = '/mnt/gosling1/bigsim_products/AbacusCosmos_1100box_planck_products/'
phases = range(20)
store_dir = '/home/dyt/store/'
save_dir = os.path.join(store_dir, sim_name_prefix+tagout)
cosmology = 0
redshift = 0.5  # one redshift at a time instead of 'all'

N_threads = 20
model_names = ['gen_vel1', 'gen_base1']

filedir = os.path.join(save_dir,
                       '{}_{:02}-coadd'.format(sim_name_prefix, cosmology),
                       'z{}'.format(redshift))
for polydeg, rmin in product(['1', '2', '3', '3p'], [20, 30, 40, 50]):
    print('Fitting with polydeg = {}, rmin = {}'.format(polydeg, rmin))
    list_of_inputs = []
    for model_name in model_names:
        xi_type = 'post-recon-ite-15.0_hmpc'
        for phase in phases:  # list of inputs for parallelisation
            path_xi_0 = os.path.join(
                filedir,
                '{}-auto-fftcorr_xi_0-{}-jackknife_{}-coadd.txt'
                .format(model_name, xi_type, phase))
            path_xi_2 = os.path.join(
                filedir,
                '{}-auto-fftcorr_xi_2-{}-jackknife_{}-coadd.txt'
                .format(model_name, xi_type, phase))
            path_cov = os.path.join(
                filedir,
                '{}-cross-xi_monoquad-cov-smu-post-recon-std-sr.txt'
                .format(model_name))
            fout_tag = '{}-{}-{}'.format(model_name, phase, xi_type)
            list_of_inputs.append(
                [path_xi_0, path_xi_2, path_cov, fout_tag, polydeg, rmin])
    with closing(MyPool(processes=N_threads, maxtasksperchild=1)) as p:
        p.map(baofit, list_of_inputs)
    p.close()
    p.join()

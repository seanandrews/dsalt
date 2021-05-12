"""
Generate a synthetic ALMA dataset.

"""

import os, sys, time
import numpy as np
import const as c_
import mconfig as in_
from cube_parser import cube_parser


# file parsing
tpre = 'obs_templates/'+in_.template


### Decide whether to create or use an existing observational template
if np.logical_and(os.path.exists(tpre+'.uvfits'), 
                  os.path.exists(tpre+'.params')):

    # load the parameters for the existing template
    tp = np.loadtxt(tpre+'.params', dtype=str).tolist()

    # if the parameters are the same, use the existing one; otherwise, save
    # the old one under a previous name and proceed
    ip = [in_.RA, in_.DEC, in_.date, in_.HA, in_.config, in_.ttotal, 
          in_.integ, in_.spec_oversample]
    if tp == ip:
        print('This template already exists...using the files from %s' % \
              (time.ctime(os.path.getctime(tpre+'.uvfits'))))
        gen_template = True	#False
    else:
        gen_template = True
        if in_.overwrite_template:
            print('Removing old template with same name, but different params')
            os.system('rm '+tpre+'.uvfits '+tpre+'.params')
            os.system('rm obs_templates/sims/'+in_.template+'*')
        else:
            print('Renaming old template with same name, but different params')
            old_t = time.ctime(os.path.getctime(tpre+'.uvfits'))
            os.system('mv '+tpre+'.uvfits '+tpre+'_'+old_t+'.uvfits') 
            os.system('mv '+tpre+'.params '+tpre+'_'+old_t+'.params')
            os.system('mv obs_templates/sims/'+in_.template+' '+ \
                      'obs_templates/sims/'+in_.template+'_'+old_t)
            
else:
    gen_template = True


### Generate the mock observations template (if necessary)
if gen_template: 

    # Create a template parameters file for records
    ip = [in_.RA, in_.DEC, in_.date, in_.HA, in_.config, in_.ttotal, 
          in_.integ, in_.spec_oversample]
    f = open(tpre+'.params', 'w')
    [f.write(ip[i]+'\n') for i in range(7)]
    f.write(str(ip[-1]))
    f.close()

    # Set the over-sampled (LSRK) channels for calculating the template
    dv0 = (c_.c * in_.dfreq0 / in_.restfreq) / in_.spec_oversample
    nch = 2 * np.int(in_.vspan / dv0) + 1
    vel = in_.vsys + dv0 * (np.arange(nch) - np.int(nch/2) + 1)

    # Convert target coordinates into decimal degrees
    RA_pieces = [np.float(in_.RA.split(':')[i]) for i in np.arange(3)]
    RAdeg = 15 * np.sum(np.array(RA_pieces) / [1., 60., 3600.])
    DEC_pieces = [np.float(in_.DEC.split(':')[i]) for i in np.arange(3)]
    DECdeg = np.sum(np.array(DEC_pieces) / [1., 60., 3600.])

    # Generate a dummy model .FITS cube
    cube_parser(in_.pars, FOV=8, Npix=256, dist=150, r_max=300, 
                restfreq=in_.restfreq, RA=RAdeg, DEC=DECdeg, Vsys=in_.vsys,
                vel=vel, outfile=tpre+'.fits')

    # Generate the (u,v) tracks and spectra on starting integration LSRK frame
    os.system('casa --nologger --nologfile -c CASA_scripts/mock_obs.py')

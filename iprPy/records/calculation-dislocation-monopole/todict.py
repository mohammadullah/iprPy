from DataModelDict import DataModelDict as DM

import atomman as am
import atomman.unitconvert as uc
import numpy as np

from iprPy.tools import aslist

def todict(record, full=True, flat=False):

    model = DM(record)

    calc = model['calculation-dislocation-monopole']
    params = {}
    params['calc_key'] =            calc['key']
    params['calc_script'] =         calc['calculation']['script']
    params['iprPy_version'] =       calc['calculation']['iprPy-version']
    params['LAMMPS_version'] =      calc['calculation']['LAMMPS-version']
    
    params['energytolerance']=      calc['calculation']['run-parameter']['energytolerance']
    params['forcetolerance'] =      calc['calculation']['run-parameter']['forcetolerance']
    params['maxiterations']  =      calc['calculation']['run-parameter']['maxiterations']
    params['maxevaluations'] =      calc['calculation']['run-parameter']['maxevaluations']
    params['maxatommotion']  =      calc['calculation']['run-parameter']['maxatommotion']
    
    params['annealtemperature'] =   calc['calculation']['run-parameter']['annealtemperature']

    sizemults =              calc['calculation']['run-parameter']['size-multipliers']
    
    params['potential_LAMMPS_key'] =    calc['potential-LAMMPS']['key']
    params['potential_LAMMPS_id'] =     calc['potential-LAMMPS']['id']
    params['potential_key'] =           calc['potential-LAMMPS']['potential']['key']
    params['potential_id'] =            calc['potential-LAMMPS']['potential']['id']
    
    params['load_file'] =       calc['system-info']['artifact']['file']
    params['load_style'] =      calc['system-info']['artifact']['format']
    params['load_options'] =    calc['system-info']['artifact']['load_options']
    params['family'] =          calc['system-info']['family']
    symbols =                   aslist(calc['system-info']['symbol'])
    
    params['dislocation_key'] = calc['dislocation-monopole']['key']
    params['dislocation_id'] =  calc['dislocation-monopole']['id']
    
    if flat is True:
        params['a_mult1'] = sizemults['a'][0]
        params['a_mult2'] = sizemults['a'][1]
        params['b_mult1'] = sizemults['b'][0]
        params['b_mult2'] = sizemults['b'][1]
        params['c_mult1'] = sizemults['c'][0]
        params['c_mult2'] = sizemults['c'][1]
        params['symbols'] = ' '.join(symbols)
    else:
        params['sizemults'] = np.array([sizemults['a'], sizemults['b'], sizemults['c']])
        params['symbols'] = symbols
    
    params['status'] = calc.get('status', 'finished')
    
    if full is True:
        if params['status'] == 'error':
            params['error'] = calc['error']

        elif params['status'] == 'not calculated':
            pass
        else:
            params['preln'] = uc.value_unit(calc['Stroh-pre-ln-factor'])

            if flat is True:
                for C in calc['elastic-constants'].aslist('C'):
                    params['C'+str(C['ij'][0])+str(C['ij'][2])] = uc.value_unit(C['stiffness'])
                for K in calc['Stroh-K-tensor']:
                    params['K'+str(K['ij'][0])+str(K['ij'][2])] = uc.value_unit(K['stiffness'])
            else:
                params['C'] = am.ElasticConstants(model=model)
                params['K_tensor'] = np.empty((3,3))            
                for kterm in calc['Stroh-K-tensor']:
                    i = int(kterm['ij'][0]) - 1
                    j = int(kterm['ij'][2]) - 1
                    params['K_tensor'][i,j] = uc.value_unit(kterm['coefficient'])
                    params['K_tensor'][j,i] = uc.value_unit(kterm['coefficient'])

    return params 
    
import io
#from abc import ABC, abstractmethod

import os
#os.environ['OCTAVE_EXECUTABLE']= 'E:\octave\Octave-5.2.0\mingw64\\bin\octave-cli.exe'

class CNA_Methods: #(ABC):
    """
    convenience methods for cnapy
    """

    def read_cnapy_model(self):
        self.eval("load cobra_model.mat", nargout=0)
        self.eval("cnap= CNAcobra2cna(cbmodel);", nargout=0)
        
try:
    import matlab.engine
    from matlab.engine import MatlabEngine

    class CNAMatlabEngine(CNA_Methods, MatlabEngine):
        def __init__(self, cna_path):
            """
            have go to via MatlabFuture because the MatlabEngine constructor requires a Matlab handle
            """
            future = matlab.engine.matlabfuture.MatlabFuture(option = "-nodesktop")
            super().__init__(matlab.engine.pythonengine.getMATLAB(future._future))
            self.cd(cna_path)
            self.startcna(1, nargout = 0)

        def get_reacID(self):
            self.eval("reac_id = cellstr(cnap.reacID);", nargout= 0)
            reac_id = self.workspace['reac_id']
            return reac_id

except:
    print('Matlab engine not available.')

try:
    import oct2py

    class CNAoctaveEngine(CNA_Methods, oct2py.Oct2Py):
        def __init__(self, cna_path):
            super().__init__()
            self.cd(cna_path)
            self.startcna(1)

        def get_reacID(self):
            self.eval("reac_id = cellstr(cnap.reacID);")
            reac_id = self.pull('reac_id')
            reac_id = reac_id.tolist()
            return reac_id

except:
    print('Octave is not available.')

def run_tests():
    cna_path= 'E:\gwdg_owncloud\CNAgit\CellNetAnalyzer'
    m = CNAMatlabEngine(cna_path)
    m.read_cnapy_model()
    a= m.get_reacID()
    o = CNAoctaveEngine(cna_path)
    o.read_cnapy_model()
    b= o.get_reacID()
    # advanced stuff
    ptr= o.get_pointer('cnap')
    o.CNAcomputeEFM(ptr)

    # m.eval('x=SimpleClass()', nargout=0)
    # x= m.workspace['x']
    # m.foo(x, nargout= 0)

    # o.eval('x=SimpleClass()', nargout=0)
    # x= o.workspace['x']
    # #o.foo(x, nargout= 0) foo is not recognized as function

    cnap = m.eval('CNA_MFNetwork(cnap);') # not needed in octave, has pointers to structs
    ems = m.CNAcomputeEFM(cnap);

    o.eval('cnap_MFNetwork= CNA_MFNetwork(cnap);')
    cnap = o.get_pointer('cnap_MFNetwork')
    ems= o.CNAcomputeEFM(cnap);

import glob
import numpy as np

from clawpack.pyclaw.solution import Solution
from clawpack.pyclaw.io.ascii import read_ascii as read

def frame(out):

    frames = sorted(glob.glob(out + '/fort.q*'))

    lastframe = frames[-1]

    return int(lastframe[-4:])

def error(out1, out2):

    frame1 = frame(out1)
    frame2 = frame(out2)

    sol1 = Solution()
    read(sol1, frame1, path=out1)

    sol2 = Solution()
    read(sol2, frame2, path=out2)

    return abs(sol2.q[0,:]-sol1.q[0,:]).max()


#reference = 'sdcgl17_dt002.d'
#reference = 'rk104_dt00002.d'
reference = 'sdcgl07_dt001.d'

for run in sorted(glob.glob('*.d')):
    if run == reference:
        continue

    print run, np.log10(error(run, reference))

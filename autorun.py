"""PyPFASST shockbubble auto-run."""

import numpy as np
import numpy.fft as fft
import pfshockbubble
import clawpack.pyclaw as pyclaw

from shockbubble import qinit

class Mock():
  pass


def autorun(mx=160, my=40, **kwargs):
  """Auto-run parameters."""

  state = Mock()
  state.patch = Mock()

  state.q = np.asfortranarray(np.zeros((5, mx, my)))

  x = pyclaw.Dimension('x',0.0,2.0,mx)
  y = pyclaw.Dimension('y',0.0,0.5,my)
  state.grid = pyclaw.Domain([x,y]).patches[0]

  qinit(state)

  q0 = state.q

  dt = 0.002

  return {
    'dt':          dt,
    'iterations':  3,
    'nnodes':      3,
    'qtype':       'GL',
    'feval':       pfshockbubble.PFASSTShockBubble,
    'initial':     q0.flatten('f'),
    # 'interpolate': pfshockbubble.interpolate,
    # 'restrict':    pfshockbubble.restrict,
    'dump_compress': False,
    'dump_predictor': False,
    'refine': [ (1, 1), (2, 1), (4, 1) ],
    }


def pyclaw_write_hook(level, state, **kwargs):

  print "dump step: ", state.step+1
  level.feval.solution.write(state.step+1, path=level.feval.clawoutput)


def setup(pf, sweeps=2, outdir='', **kwargs):
  """Final auto-run setup."""

  if outdir:
    pf.levels[0].feval.clawoutput = outdir
    pf.add_hook(0, 'end-step', pyclaw_write_hook)

  if len(pf.levels) > 1:
    pf.levels[-1].sweeps = sweeps

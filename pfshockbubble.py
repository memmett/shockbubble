
import pfasst.imex
from shockbubble import *

class PFASSTShockBubble(pfasst.imex.IMEXFEval):

  def __init__(self, shape=None, mx=160, my=40, use_petsc=False, **kwargs):

    super(PFASSTShockBubble, self).__init__()

    if use_petsc:
        import clawpack.petclaw as pyclaw
    else:
        import clawpack.pyclaw as pyclaw

    import clawpack.riemann as riemann

    solver = pyclaw.SharpClawSolver2D()
    solver.dq_src=dq_Euler_radial
    solver.weno_order=5
    solver.lim_type=2

    solver.rp          = riemann.rp2_euler_5wave
    solver.cfl_max     = 0.5
    solver.cfl_desired = 0.45
    solver.num_waves   = 5
    solver.bc_lower[0]=pyclaw.BC.custom
    solver.bc_upper[0]=pyclaw.BC.extrap
    solver.bc_lower[1]=pyclaw.BC.wall
    solver.bc_upper[1]=pyclaw.BC.extrap

    solver.aux_bc_lower[0]=pyclaw.BC.extrap
    solver.aux_bc_upper[0]=pyclaw.BC.extrap
    solver.aux_bc_lower[1]=pyclaw.BC.extrap
    solver.aux_bc_upper[1]=pyclaw.BC.extrap

    # initialize domain
    x = pyclaw.Dimension('x', 0.0, 2.0, mx)
    y = pyclaw.Dimension('y', 0.0, 0.5, my)
    domain = pyclaw.Domain([x, y])
    state = pyclaw.State(domain, 5, 1)

    state.problem_data['gamma']  = gamma
    state.problem_data['gamma1'] = gamma1

    qinit(state)
    auxinit(state)

    solver.user_bc_lower = shockbc

    solution = pyclaw.Solution(state, domain)

    solver.setup(solution)

    self.solution = solution
    self.solver = solver
    self.state = state

    self.shape  = (5*mx*my,)
    self.size   = 5*mx*my
    self.qshape = (5, mx, my)


  def f1_evaluate(self, q, t, f1, **kwargs):

    if np.any(np.isnan(q)):
      raise ValueError("NaNs")

    self.state.q[...] = q.reshape(self.qshape, order='f')
    f1[...] = self.solver.dqdt(self.state)

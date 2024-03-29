"""Shockbubble example."""

import numpy as np

gamma = 1.4
gamma1 = gamma - 1.


def qinit(state,x0=0.5,y0=0.,r0=0.2,rhoin=0.1,pinf=5.):
    """Initial condition."""
    
    grid = state.grid

    rhoout = 1.
    pout   = 1.
    pin    = 1.

    rinf = (gamma1 + pinf*(gamma+1.))/ ((gamma+1.) + gamma1*pinf)
    vinf = 1./np.sqrt(gamma) * (pinf - 1.) / np.sqrt(0.5*((gamma+1.)/gamma) * pinf+0.5*gamma1/gamma)
    einf = 0.5*rinf*vinf**2 + pinf/gamma1
    
    # Create an array with fortran native ordering
    x =grid.x.centers
    y =grid.y.centers
    Y,X = np.meshgrid(y,x)
    r = np.sqrt((X-x0)**2 + (Y-y0)**2)

    state.q[0,:,:] = rhoin*(r<=r0) + rhoout*(r>r0)
    state.q[1,:,:] = 0.
    state.q[2,:,:] = 0.
    state.q[3,:,:] = (pin*(r<=r0) + pout*(r>r0))/gamma1
    state.q[4,:,:] = 1.*(r<=r0)

    
def auxinit(state):
    """Auxiliary data.

    The auxiliary data is set to:

      aux[1,i,j] = y-coordinate of cell centers for cylindrical source
                   terms

    """
    x=state.grid.x.centers
    y=state.grid.y.centers
    for j,ycoord in enumerate(y):
        state.aux[0,:,j] = ycoord


def shockbc(state,dim,t,qbc,num_ghost):
    """Incoming shock at left boundary."""

    for (i,state_dim) in enumerate(state.patch.dimensions):
        if state_dim.name == dim.name:
            dim_index = i
            break
      
    if (state.patch.dimensions[dim_index].lower == 
                        state.grid.dimensions[dim_index].lower):

        pinf=5.
        rinf = (gamma1 + pinf*(gamma+1.))/ ((gamma+1.) + gamma1*pinf)
        vinf = 1./np.sqrt(gamma) * (pinf - 1.) / np.sqrt(0.5*((gamma+1.)/gamma) * pinf+0.5*gamma1/gamma)
        einf = 0.5*rinf*vinf**2 + pinf/gamma1

        for i in xrange(num_ghost):
            qbc[0,i,...] = rinf
            qbc[1,i,...] = rinf*vinf
            qbc[2,i,...] = 0.
            qbc[3,i,...] = einf
            qbc[4,i,...] = 0.


def step_Euler_radial(solver,state,dt):
    """Geometric source terms for Euler equations with radial symmetry.

    Integrated using a 2-stage, 2nd-order Runge-Kutta method.  This is
    a Clawpack-style source term routine.

    """
    
    dt2 = dt/2.
    ndim = 2

    aux=state.aux
    q = state.q

    rad = aux[0,:,:]

    rho = q[0,:,:]
    u   = q[1,:,:]/rho
    v   = q[2,:,:]/rho
    press  = gamma1 * (q[3,:,:] - 0.5*rho*(u**2 + v**2))

    qstar = np.empty(q.shape)

    qstar[0,:,:] = q[0,:,:] - dt2*(ndim-1)/rad * q[2,:,:]
    qstar[1,:,:] = q[1,:,:] - dt2*(ndim-1)/rad * rho*u*v
    qstar[2,:,:] = q[2,:,:] - dt2*(ndim-1)/rad * rho*v*v
    qstar[3,:,:] = q[3,:,:] - dt2*(ndim-1)/rad * v * (q[3,:,:] + press)

    rho = qstar[0,:,:]
    u   = qstar[1,:,:]/rho
    v   = qstar[2,:,:]/rho
    press  = gamma1 * (qstar[3,:,:] - 0.5*rho*(u**2 + v**2))

    q[0,:,:] = q[0,:,:] - dt*(ndim-1)/rad * qstar[2,:,:]
    q[1,:,:] = q[1,:,:] - dt*(ndim-1)/rad * rho*u*v
    q[2,:,:] = q[2,:,:] - dt*(ndim-1)/rad * rho*v*v
    q[3,:,:] = q[3,:,:] - dt*(ndim-1)/rad * v * (qstar[3,:,:] + press)


def dq_Euler_radial(solver,state,dt):
    """Geometric source terms for Euler equations with radial symmetry.
    
    Integrated using a 2-stage, 2nd-order Runge-Kutta method.  This is
    a SharpClaw-style source term routine.

    """
    
    ndim = 2

    q   = state.q
    aux = state.aux

    rad = aux[0,:,:]

    rho = q[0,:,:]
    u   = q[1,:,:]/rho
    v   = q[2,:,:]/rho
    press  = gamma1 * (q[3,:,:] - 0.5*rho*(u**2 + v**2))

    dq = np.empty(q.shape)

    dq[0,:,:] = -dt*(ndim-1)/rad * q[2,:,:]
    dq[1,:,:] = -dt*(ndim-1)/rad * rho*u*v
    dq[2,:,:] = -dt*(ndim-1)/rad * rho*v*v
    dq[3,:,:] = -dt*(ndim-1)/rad * v * (q[3,:,:] + press)
    dq[4,:,:] = 0

    return dq

def shockbubble(use_petsc=False, solver_type='sharpclaw', kernel_language='Fortran',
                dt=0.001, tfinal=0.02, outdir='test', restart=False):
    """Solve the Euler equations of compressible fluid dynamics.

    This example involves a bubble of dense gas that is impacted by a
    shock.

    """

    from clawpack import riemann

    if use_petsc:
        import clawpack.petclaw as pyclaw
    else:
        from clawpack import pyclaw

    if kernel_language != 'Fortran':
        raise Exception('Unrecognized value of kernel_language for Euler Shockbubble')

    if solver_type=='sharpclaw':
        solver = pyclaw.SharpClawSolver2D()
        solver.dq_src=dq_Euler_radial
        solver.weno_order=5
        solver.lim_type=2
    else:
        solver = pyclaw.ClawSolver2D()
        solver.limiters = [4,4,4,4,2]
        solver.step_source=step_Euler_radial
        solver.source_split = 1

    solver.rp          = riemann.rp2_euler_5wave
    solver.cfl_max     = 0.5
    solver.cfl_desired = 0.45
    solver.num_waves   = 5
    solver.dt_initial  = 0.005

    solver.user_bc_lower = shockbc
    solver.bc_lower[0] = pyclaw.BC.custom
    solver.bc_upper[0] = pyclaw.BC.extrap
    solver.bc_lower[1] = pyclaw.BC.wall
    solver.bc_upper[1] = pyclaw.BC.extrap

    # aux variable in ghost cells doesn't matter
    solver.aux_bc_lower[0] = pyclaw.BC.extrap
    solver.aux_bc_upper[0] = pyclaw.BC.extrap
    solver.aux_bc_lower[1] = pyclaw.BC.extrap
    solver.aux_bc_upper[1] = pyclaw.BC.extrap

    # initial condition or restart
    if restart:

        initial_solution = pyclaw.Solution(1, path=restart)
        initial_solution.t = 0.0

        for state in initial_solution.states:
            state.problem_data['gamma'] = gamma
            state.problem_data['gamma1'] = gamma1
            auxinit(state)

    else:

        mx, my = 160, 40
        x = pyclaw.Dimension('x', 0.0, 2.0, mx)
        y = pyclaw.Dimension('y', 0.0, 0.5, my)
        num_eqn = 5
        num_aux = 1
        
        domain  = pyclaw.Domain([x, y])
        state   = pyclaw.State(domain, num_eqn, num_aux)

        state.problem_data['gamma']  = gamma
        state.problem_data['gamma1'] = gamma1

        auxinit(state)
        qinit(state)
        
        initial_solution = pyclaw.Solution(state, domain)


    solver.dt_variable = False
    solver.dt_initial  = dt
    solver.max_steps   = 1e9

    claw = pyclaw.Controller()
    claw.keep_copy = True
    claw.tfinal    = tfinal
    claw.solution  = initial_solution
    claw.solver    = solver
    claw.outdir    = outdir
    claw.num_output_times = int(tfinal/dt)

    # Solve
    status = claw.run()

    return claw.frames[claw.num_output_times].state


if __name__=="__main__":
    from clawpack.pyclaw.util import run_app_from_main
    import cProfile

    cProfile.runctx('output = run_app_from_main(shockbubble)',
                    globals(), locals(), 'shprof')

    # if pf.mpi.comm.rank == 0:
    print '\n==== profiling info ====\n'
    import pstats
    p = pstats.Stats('shprof')
    p.strip_dirs().sort_stats('time').print_stats(20)

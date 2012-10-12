
import os.path
import subprocess

def run(name, method=('sdc', 'GL', 5, 5), dt=0.001, tfinal=0.6, order=-1, restart='start'):
    """Run the shockbubble example."""

    if os.path.exists(name + '.d'):
        print "directory '%s' already exists, skipping..." % name
        return

    if method[0] == 'sdc':
        cmd = '''pfautorun qtype={qtype} \
                           nnodes={nnodes} \
                           iterations={iterations} \
                           dt={{dt}} \
                           tend={{tfinal}} \
                           outdir={{name}}.d \
                           profile=True 1> {{name}}.out'''.format(
            qtype=method[1], nnodes=method[2], iterations=method[3])
    else:
        cmd = '''python shockbubble.py dt={dt} outdir={name}.d tfinal={tfinal} restart={restart} 1> {name}.out'''


    cmd = cmd.format(dt=dt, tfinal=tfinal, name=name, restart=restart)

    print 'running: %s' % name
    subprocess.call(cmd, shell=True)
    # subprocess.Popen(cmd, shell=True)

run('sdcgl03_dt001', method=('sdc', 'GL', 3, 4))
# run('sdcgl05_dt001', method=('sdc', 'GL', 5, 8))
# run('sdcgl07_dt001', method=('sdc', 'GL', 7, 12))
# run('sdcgl09_dt001', method=('sdc', 'GL', 9, 16))

# # run('rk104_dt001', method=('rk104'))
# run('rk104_dt0001', method=('rk104'), dt=0.0001)

# # run('rk104_dt00001', method=('rk104'), dt=0.00001)

# run('test1', method=('rk104'), dt=0.0001, tfinal=0.001)
# run('test2', method=('rk104'), dt=0.0001, tfinal=0.001, restart=False)

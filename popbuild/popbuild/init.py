# Import python libs
import os
import uuid
import subprocess
import shutil
import tempfile


def __init__(hub):
    hub.popbuild.BUILDS = {}


def cli(hub):
    '''
    Execute the routine from the CLI
    '''
    hub.pop.conf.integrate(['popbuild'], cli='popbuild', roots=True)
    hub.popbuild.init.build(
            hub.OPT['popbuild']['name'],
            hub.OPT['popbuild']['requirements'],
            hub.OPT['popbuild']['system_site'],
            hub.OPT['popbuild']['exclude'],
            hub.OPT['popbuild']['directory'],
            hub.OPT['popbuild']['dev_pyinstaller'],
            )


def new(hub, name, requirements, sys_site, exclude, directory, dev_pyinst=False):
    venv_dir = tempfile.mkdtemp()
    is_win = os.name == 'nt'
    if is_win:
        python_bin = os.path.join(venv_dir, 'Scripts', 'python')
        s_path = os.path.join(venv_dir, 'Scripts', name)
    else:
        python_bin = os.path.join(venv_dir, 'bin', 'python')
        s_path = os.path.join(venv_dir, 'bin', name)
    bname = str(uuid.uuid1())
    requirements = os.path.join(directory, requirements)
    hub.popbuild.BUILDS[bname] = {
            'name': name,
            'is_win': is_win,
            'exclude': exclude,
            'requirements': requirements,
            'sys_site': sys_site,
            'dir': os.path.abspath(directory),
            'dev_pyinst': dev_pyinst,
            'run': os.path.join(directory, 'run.py'),
            'spec': os.path.join(directory, f'{name}.spec'),
            'pybin': python_bin,
            's_path': s_path,
            'venv_dir': venv_dir,
            'vroot': os.path.join(venv_dir, 'lib'),
            'all_paths': set(),
            'imports': set(),
            'datas': set(),
            'cmd': f'{python_bin} -B -OO -m PyInstaller ',
            'pypi_args': [
                s_path,
                '--log-level=INFO',
                '--noconfirm',
                '--onefile',
                '--clean',
                ],
            }
    req = hub.popbuild.init.mk_requirements(bname)
    hub.popbuild.BUILDS[bname]['req'] = req
    return bname

def mk_requirements(hub, bname):
    opts = hub.popbuild.BUILDS[bname]
    req = os.path.join(opts['dir'], '__build_requirements.txt')
    with open(opts['requirements'], 'r') as rfh:
        data = rfh.read()
    with open(req, 'w+') as wfh:
        wfh.write(data)
    return req


def build(hub, name, requirements, sys_site, exclude, directory, dev_pyinst=False):
    bname = hub.popbuild.init.new(name, requirements, sys_site, exclude, directory, dev_pyinst)
    hub.popbuild.venv.create(bname)
    hub.popbuild.build.make(bname)
    hub.popbuild.venv.scan(bname)
    hub.popbuild.venv.mk_adds(bname)
    hub.popbuild.inst.mk_spec(bname)
    hub.popbuild.inst.call(bname)
    hub.popbuild.post.report(bname)
    hub.popbuild.post.clean(bname)


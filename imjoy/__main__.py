import sys
import os
import subprocess

if __name__ == '__main__':
    if not 'Anaconda' in sys.version:
        try:
            subprocess.call(["conda", "-V"])
        except OSError as e:
            sys.exit('Sorry, ImJoy plugin engine can only run with Anaconda.')

    if sys.version_info > (3, 0):
        # running in python 3
        try:
            import pkg_resources  # part of setuptools
            version = pkg_resources.require("imjoy")[0].version
            print('ImJoy Python Plugin Engine (version {})'.format(version))
        except:
            pass
        from .pluginEngine import *
        web.run_app(app)
    else:
        # running in python 2
        print('ImJoy needs to run in Python 3.6+, bootstrapping with conda ...')
        imjoy_requirements = ['requests','gevent','websocket-client-py3','python-socketio','aiohttp', 'numpy', '.']
        ret = os.system('conda create -y -n imjoy python=3.6 anaconda')
        if ret == 0:
            print('conda environment is now ready, installing pip requirements and start the engine...')
        else:
            print('conda environment failed to setup, please make sure you are running in a conda environment...')
        requirements = imjoy_requirements
        pip_cmd = "pip install -U "+" ".join(requirements)
        pip_cmd = "source activate imjoy || activate imjoy && " + pip_cmd + " && python -m imjoy"

        ret = os.system(pip_cmd)
        if ret != 0:
            print('ImJoy failed with exit code: '+str(ret))

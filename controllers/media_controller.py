import os
os.environ["PYTHON_VLC_MODULE_PATH"] = r"C:\Program Files\VideoLAN\VLC"
os.environ["PATH"] = os.environ["PYTHON_VLC_MODULE_PATH"] + os.pathsep + os.environ["PATH"]
# disk_image_manager_app


### platform requirements

$ sudo apt install dcfldd

#### armv7l

$ sudo apt install python3-pyqt5

### installation

$ virtualenv --system-site-packages -p /usr/bin/python3 venv/
$ source venv/bin/activate
$ python setup.py bdist_wheel
$ pip install dist/dima-VERSION-py3-none-any.whl
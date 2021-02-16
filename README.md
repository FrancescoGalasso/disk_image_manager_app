# disk_image_manager_app

This project is a linux-platform tool to flash OS images onto SD cards and USB drives safely and easily.

**PyQt5** was chosen for the graphical interface.

**dcfldd**, a wrapper for **dd**, was chosen for the OS image writing process. 


## Platform requirements

This project required dcfldd [man dcfldd](https://linux.die.net/man/1/dcfldd); the project is intended to be orchestrated via [supervisor](http://supervisord.org/)

```
	$ sudo apt install dcfldd supervisor
```

Modify supervisord.conf in order to add the dima supervisor folder path

```
	$ sudo nano /etc/supervisor/supervisord.conf
	$ cat /etc/supervisor/supervisord.conf
	; supervisor config file

	[unix_http_server]
	chown=galasso
	file=/var/run/supervisor.sock   ; (the path to the socket file)
	chmod=0700                       ; sockef file mode (default 0700)

	[supervisord]
	environment=PYTHONDONTWRITEBYTECODE=1
	logfile=/var/log/supervisor/supervisord.log ; (main log file;default $CWD/supervisord.log)
	pidfile=/var/run/supervisord.pid ; (supervisord pidfile;default supervisord.pid)
	childlogdir=/var/log/supervisor            ; ('AUTO' child log dir, default $TEMP)

	; the below section must remain in the config file for RPC
	; (supervisorctl/web interface) to work, additional interfaces may be
	; added by defining them in separate rpcinterface: sections
	[rpcinterface:supervisor]
	supervisor.rpcinterface_factory = supervisor.rpcinterface:make_main_rpcinterface

	[supervisorctl]
	serverurl=unix:///var/run/supervisor.sock ; use a unix:// URL  for a unix socket

	; The [include] section can just contain the "files" setting.  This
	; setting can list multiple files (separated by whitespace or
	; newlines).  It can also contain wildcards.  The filenames are
	; interpreted as relative to this file.  Included files *cannot*
	; include files themselves.

	[include]
	files = /opt/dima/conf/supervisor/*.conf

```


**NOTE**
For armv7l architecture, it is also required the installation of PyQt5 via apt
```
	$ sudo apt install python3-pyqt5 -y
```


## installation

The installation (on host or on target) is done through the creation of the wheel package and its installation via pip.

this project is a pip-package (a python wheel) containing the following python modules (mapping the 'logical' domains of the software stack):

### the modules:

* **src/dima/dima_backend**: contains everything related to the dima engine (python wrapper for dcfldd and for lsblk)
* **src/dima/dima_frontend**: a pyqt5 based application  

### the **conf** dir:

the directory **conf** in the root of the project is NOT part of the package itself: (due to the fact that pip install procedure is meant NOT to alter the system configuration) we add (in *install* action of **make.py**) a step in order to deploy what is needed for manage processes on the system. 
Everything useful for this, is contained in the **conf** dir.


### The **make.py**

the script **make.py** implements some utilities or tools, useful in development, in order to:

* create the virtual env 
* install the package
* deploy the configurations on target and on host platform
* install the package in editable mode (aka development mode) onto the host platform itself.


For the description of cmdline options, try:
```
    $ python3 make.py -h
	usage: make.py [-h] [-l LOG_LEVEL] [-t TARGET_CREDENTIALS] [-a TARGET_ARCHITECTURE] [-i] [-d] [-b] [-e] [-I] [-M] [-m] [-c] [-C]

	development tool for build/install.

	optional arguments:
	  -h, --help            show this help message and exit
	  -l LOG_LEVEL, --log_level LOG_LEVEL
	                        level of verbosity in logging messages default: INFO.
	  -t TARGET_CREDENTIALS, --target_credentials TARGET_CREDENTIALS
	                        default: "admin@192.168.1.100".
	  -a TARGET_ARCHITECTURE, --target_architecture TARGET_ARCHITECTURE
	                        RBPi: "armv7l" default: "x86_64".
	  -i, --ignore_requires
	                        if not None, ignore_requires in installing. default: "None".
	  -d, --dry_run         dry run: if not None, just test, do nothing. default: "None".
	  -b, --build           action: build the wheel.
	  -e, --install_editable
	  -I, --install_target
	  -M, --makedirs_on_target
	  -m, --makedirs_on_host
	  -c, --create_venv_on_target
	  -C, --deploy_conf_to_target


```

and look at the content of **make.py** to know more.

### The "scripts" (or bin/ dir)

The installation procedure adds the following commands to the environment -see [SCRIPTS in setup.py](./setup.py)-:

+ dima       (launches the dima process)

(And these are the commands used by the *supervisord* to start processes, see the **conf** file). 


## Dima setup and installation guide using make.py

#### Create dima dirs on target (use only on first installation)

```
	$ python3 make.py -t "admin@192.168.0.100" -M
	[2021-02-03 16:52:54,710]INFO main() make.py:146 args:Namespace(build=None, create_venv_on_target=None, deploy_conf_to_target=None, dry_run=None, ignore_requires=None, install_editable=None, install_target=None, log_level='INFO', makedirs_on_host=None, makedirs_on_target=1, target_architecture='x86_64', target_credentials='admin@192.168.0.100')
	[2021-02-03 16:52:54,710]WARNING main() make.py:147 see also command log msgs in /opt/PERSONAL_PROJECTS/disk_image_manager_app/make.err.out
	[2021-02-03 16:52:54,710]INFO exec_() make.py:52 dry:None cmd_:ssh admin@192.168.0.100 "if [ ! -e /opt/dima ]; then sudo mkdir -p /opt/dima && sudo chown -R admin:admin /opt/dima ;fi"
	[2021-02-03 16:52:55,071]INFO exec_() make.py:55 ret_val:0
	[2021-02-03 16:52:55,071]INFO exec_() make.py:52 dry:None cmd_:ssh admin@192.168.0.100 "if [ ! -e /opt/dima/venv ]; then mkdir -p /opt/dima/venv ;fi"
	[2021-02-03 16:52:55,357]INFO exec_() make.py:55 ret_val:0
	[2021-02-03 16:52:55,357]INFO exec_() make.py:52 dry:None cmd_:ssh admin@192.168.0.100 "if [ ! -e /opt/dima/log ]; then mkdir -p /opt/dima/log ;fi"
	[2021-02-03 16:52:55,657]INFO exec_() make.py:55 ret_val:0
	[2021-02-03 16:52:55,658]INFO exec_() make.py:52 dry:None cmd_:ssh admin@192.168.0.100 "if [ ! -e /opt/dima/tmp ]; then mkdir -p /opt/dima/tmp ;fi"
	[2021-02-03 16:52:55,917]INFO exec_() make.py:55 ret_val:0
	[2021-02-03 16:52:55,917]INFO exec_() make.py:52 dry:None cmd_:ssh admin@192.168.0.100 "if [ ! -e /opt/dima/conf ]; then mkdir -p /opt/dima/conf ;fi"
	[2021-02-03 16:52:56,142]INFO exec_() make.py:55 ret_val:0

```

#### Create virtualenv on target (use only on first installation)
Create venv specifing target credentials and target platform (RBPi armv7l)

```
    $ python3 make.py -t "admin@192.168.0.100" -c -a "armv7l"
	[2021-02-03 16:53:58,541]INFO main() make.py:146 args:Namespace(build=None, create_venv_on_target=1, deploy_conf_to_target=None, dry_run=None, ignore_requires=None, install_editable=None, install_target=None, log_level='INFO', makedirs_on_host=None, makedirs_on_target=None, target_architecture='armv7l', target_credentials='admin@192.168.0.100')
	[2021-02-03 16:53:58,541]WARNING main() make.py:147 see also command log msgs in /opt/PERSONAL_PROJECTS/disk_image_manager_app/make.err.out
	[2021-02-03 16:53:58,542]INFO exec_() make.py:52 dry:None cmd_:ssh admin@192.168.0.100 "if [ ! -e /opt/dima/venv ]; then virtualenv --system-site-packages -p /usr/bin/python3 /opt/dima/venv ;fi"
	[2021-02-03 16:53:58,825]INFO exec_() make.py:55 ret_val:0
```

#### Deploy conf on target

```
	$ python3 make.py -t "admin@192.168.0.100" -C
	[2021-02-03 17:21:46,509]INFO main() make.py:146 args:Namespace(build=None, create_venv_on_target=None, deploy_conf_to_target=1, dry_run=None, ignore_requires=None, install_editable=None, install_target=None, log_level='INFO', makedirs_on_host=None, makedirs_on_target=None, target_architecture='x86_64', target_credentials='admin@192.168.0.100')
	[2021-02-03 17:21:46,509]WARNING main() make.py:147 see also command log msgs in /opt/PERSONAL_PROJECTS/disk_image_manager_app/make.err.out
	[2021-02-03 17:21:46,509]INFO exec_() make.py:52 dry:None cmd_:ssh admin@192.168.0.100 "if [ ! -e /opt/dima/conf/supervisor/ ]; then mkdir -p /opt/dima/conf/supervisor/ ;fi"
	[2021-02-03 17:21:46,753]INFO exec_() make.py:55 ret_val:0
	[2021-02-03 17:21:46,753]INFO exec_() make.py:52 dry:None cmd_:scp /opt/PERSONAL_PROJECTS/disk_image_manager_app/conf/supervisor.target.conf admin@192.168.0.100:/opt/dima/conf/supervisor/dima.conf
	[2021-02-03 17:21:46,970]INFO exec_() make.py:55 ret_val:0

```

#### Build the wheel on host

```
	$ python3 make.py -b
	[2021-02-03 14:48:46,000]INFO main() make.py:140 args:Namespace(app_settings='app_settings.production', build=1, create_venv_on_target=None, deploy_conf_to_target=None, dry_run=None, ignore_requires=None, install_editable=None, install_target=None, log_level='INFO', makedirs_on_host=None, makedirs_on_target=None, target_credentials='admin@192.168.0.100')
	[2021-02-03 14:48:46,000]WARNING main() make.py:141 see also command log msgs in /opt/PERSONAL_PROJECTS/disk_image_manager_app/make.err.out
	[2021-02-03 14:48:46,001]INFO exec_() make.py:52 dry:None cmd_:cd /opt/PERSONAL_PROJECTS/disk_image_manager_app;. /opt/PERSONAL_PROJECTS/disk_image_manager_app/venv/bin/activate; python setup.py bdist_wheel
	[2021-02-03 14:48:46,439]INFO exec_() make.py:55 ret_val:0
	[2021-02-03 14:48:46,439]INFO exec_() make.py:52 dry:None cmd_:ls -l /opt/PERSONAL_PROJECTS/disk_image_manager_app/dist/dima-0.2.0-py3-none-any.whl
	[2021-02-03 14:48:46,441]INFO exec_() make.py:55 ret_val:0
```


#### Install dima on target

```
	$ python3 make.py -t "admin@192.168.0.100" -I
	[2021-02-03 14:49:00,131]INFO main() make.py:140 args:Namespace(app_settings='app_settings.production', build=None, create_venv_on_target=None, deploy_conf_to_target=None, dry_run=None, ignore_requires=None, install_editable=None, install_target=1, log_level='INFO', makedirs_on_host=None, makedirs_on_target=None, target_credentials='admin@192.168.0.100')
	[2021-02-03 14:49:00,131]WARNING main() make.py:141 see also command log msgs in /opt/PERSONAL_PROJECTS/disk_image_manager_app/make.err.out
	[2021-02-03 14:49:00,131]INFO exec_() make.py:52 dry:None cmd_:scp /opt/PERSONAL_PROJECTS/disk_image_manager_app/dist/dima-0.2.0-py3-none-any.whl admin@192.168.0.100:/opt/dima/tmp/
	[2021-02-03 14:49:00,447]INFO exec_() make.py:55 ret_val:0
	[2021-02-03 14:49:00,548]INFO exec_() make.py:52 dry:None cmd_:ssh admin@192.168.0.100 ". /opt/dima/venv/bin/activate; pip uninstall -y dima"
	[2021-02-03 14:49:02,012]INFO exec_() make.py:55 ret_val:0
	[2021-02-03 14:49:02,114]INFO exec_() make.py:52 dry:None cmd_:ssh admin@192.168.0.100 ". /opt/dima/venv/bin/activate; pip install  /opt/dima/tmp/dima-0.2.0-py3-none-any.whl"
	[2021-02-03 14:49:03,696]INFO exec_() make.py:55 ret_val:0
	[2021-02-03 14:49:03,798]INFO exec_() make.py:52 dry:None cmd_:ssh admin@192.168.0.100 "sudo supervisorctl reload"
	[2021-02-03 14:49:04,445]INFO exec_() make.py:55 ret_val:0
```

#### Build the wheel on host, deploy conf files and Install dima on target

```
	$ python3 make.py -b -C -t "admin@192.168.0.100" -I
```

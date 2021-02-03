# coding: utf-8

# pylint: disable=missing-docstring
# pylint: disable=logging-format-interpolation
# pylint: disable=line-too-long
# pylint: disable=invalid-name

import sys
import os
import argparse
import time
import logging

from setup import about

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
DEPLOY_PATH = "/opt/dima"
VENV_PATH = f"{DEPLOY_PATH}/venv"
CONF_PATH = f"{DEPLOY_PATH}/conf"
LOG_PATH = f"{DEPLOY_PATH}/log"
TMP_PATH = f"{DEPLOY_PATH}/tmp"
OUT_ERR_PTH = f"{PROJECT_ROOT}/make.err.out"

VERSION = about['__version__']

def parse_arguments():

    parser = argparse.ArgumentParser(description='development tool for build/install.')
    parser.add_argument(
        '-l',
        '--log_level',
        default='INFO',
        help='level of verbosity in logging messages default: %(default)s.')
    parser.add_argument('-t', '--target_credentials', default='admin@192.168.1.100', help='default: "%(default)s".')
    parser.add_argument('-i', '--ignore_requires', help='if not None, ignore_requires in installing. default: "%(default)s".', action='store_const', const=1)
    parser.add_argument('-d', '--dry_run', action='store_const', const=True,
                        help='dry run: if not None, just test, do nothing. default: "%(default)s".')

    parser.add_argument('-b', '--build', help='action: build the wheel.', action='store_const', const=1)
    parser.add_argument('-e', '--install_editable', action='store_const', const=1)
    parser.add_argument('-I', '--install_target', action='store_const', const=1)
    parser.add_argument('-M', '--makedirs_on_target', action='store_const', const=1)
    parser.add_argument('-m', '--makedirs_on_host', action='store_const', const=1)
    parser.add_argument('-c', '--create_venv_on_target', action='store_const', const=1)
    parser.add_argument('-C', '--deploy_conf_to_target', action='store_const', const=1)

    return parser.parse_args()


def exec_(cmd_, dry):
    logging.info(f"dry:{dry} cmd_:{cmd_}")
    if not dry:
        ret_val = os.system(cmd_ + f"  >>{OUT_ERR_PTH} 2>&1 ")
        logging.info(f"ret_val:{ret_val}")


def build(args):

    cmd_ = f"cd {PROJECT_ROOT};. {PROJECT_ROOT}/venv/bin/activate; python setup.py bdist_wheel"
    exec_(cmd_, dry=args.dry_run)
    cmd_ = f"ls -l {PROJECT_ROOT}/dist/dima-{VERSION}-py3-none-any.whl"
    exec_(cmd_, dry=args.dry_run)


def install_target(args):

    tgt_cred = args.target_credentials
    ignore_requires = '--ignore-requires --no-dependencies ' if args.ignore_requires else ''

    cmds = [
        f"scp {PROJECT_ROOT}/dist/dima-{VERSION}-py3-none-any.whl {tgt_cred}:{TMP_PATH}/",
        f'ssh {tgt_cred} ". /opt/dima/venv/bin/activate; pip uninstall -y dima"',
        f'ssh {tgt_cred} ". /opt/dima/venv/bin/activate; pip install {ignore_requires} {TMP_PATH}/dima-{VERSION}-py3-none-any.whl"',
        f'ssh {tgt_cred} "sudo supervisorctl reload"',
    ]

    for cmd_ in cmds:
        exec_(cmd_, dry=args.dry_run)
        time.sleep(.1)


def install_editable(args):

    ignore_requires = '--ignore-requires --no-dependencies ' if args.ignore_requires else ''

    cmd_ = f"cd {PROJECT_ROOT};. {VENV_PATH}/bin/activate;pip uninstall -y {__app_name__}; pip install {ignore_requires} -e ./"
    exec_(cmd_, dry=args.dry_run)


def makedirs_on_target(args):

    tgt_cred = args.target_credentials

    for pth in (VENV_PATH, LOG_PATH, TMP_PATH, CONF_PATH):
        cmd_ = f'ssh {tgt_cred} "if [ ! -e {pth} ]; then mkdir -p {pth} ;fi"'
        exec_(cmd_, dry=args.dry_run)


def makedirs_on_host(args):

    os_user = os.environ.get('USER')
    cmd_ = f"if [ ! -e {DEPLOY_PATH} ]; then sudo mkdir -p {DEPLOY_PATH} && sudo chown -R {os_user}:{os_user} {DEPLOY_PATH};fi"
    exec_(cmd_, dry=args.dry_run)

    for pth in (VENV_PATH, LOG_PATH, CONF_PATH):
        cmd_ = f"if [ ! -e {pth} ]; then mkdir -p {pth} ;fi"
        exec_(cmd_, dry=args.dry_run)


def create_venv_on_target(args):

    tgt_cred = args.target_credentials

    cmd_ = f'ssh {tgt_cred} "if [ ! -e {VENV_PATH} ]; then virtualenv -p /usr/bin/python3 {VENV_PATH} ;fi"'
    exec_(cmd_, dry=args.dry_run)


def deploy_conf_to_target(args):

    tgt_cred = args.target_credentials

    cmds = [
        f'ssh {tgt_cred} "if [ ! -e {CONF_PATH}/supervisor/ ]; then mkdir -p {CONF_PATH}/supervisor/ ;fi"',
        f"scp {PROJECT_ROOT}/conf/supervisor.target.conf {tgt_cred}:/opt/dima/conf/supervisor/dima.conf",
    ]

    for cmd_ in cmds:
    # cmd_ = f"scp {PROJECT_ROOT}/conf/supervisor.target.conf {tgt_cred}:/opt/dima/conf/supervisor/dima.conf",
        exec_(cmd_, dry=args.dry_run)


def main():

    args = parse_arguments()

    fmt_ = '[%(asctime)s]%(levelname)s %(funcName)s() %(filename)s:%(lineno)d %(message)s'
    logging.basicConfig(stream=sys.stdout, level=args.log_level, format=fmt_)

    logging.info(f"args:{args}")
    logging.warning(f"see also command log msgs in {OUT_ERR_PTH}")
    with open(OUT_ERR_PTH, 'w') as f: # reset messages
        f.write(f'{time.asctime()}\n')

    if args.build:
        build(args)
    if args.install_editable:
        install_editable(args)
    if args.install_target:
        install_target(args)
    if args.makedirs_on_target:
        makedirs_on_target(args)
    if args.makedirs_on_host:
        makedirs_on_host(args)
    if args.create_venv_on_target:
        create_venv_on_target(args)
    if args.deploy_conf_to_target:
        deploy_conf_to_target(args)

main()

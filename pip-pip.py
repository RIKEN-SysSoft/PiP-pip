#!/usr/bin/env python3

import datetime
import time
import argparse
import shutil
import os
import sys
import subprocess as sp
from subprocess import PIPE

dryrun = False
log_dir = ''
msg_enter  = '>>> '
msg_exit   = '<<< '
msg_error  = '<** '
msg_prefix ='--- '
err_prefix ='ERROR:'
warn_prefix ='WARNING:'

sudo_prefix = []
docker_success=False
spack_success=False
spack_path = ''
query_prefix=False

flag_multi=False

def redhat_version():
    with open( '/etc/redhat-release', mode='r' ) as f:
        l = f.readline().split().pop(3).split('.').pop(0)
    return int( l )

def cpu_arch():
    return sp.check_output( [ 'uname', '-m' ] ).decode().split().pop(0)

def log( list, log_fs ):
    last = list[-1]
    for msg in list:
        if msg != last:
            print( msg, end=' ', flush=True )
            if not dryrun:
                print( msg, end=' ', file=log_fs )
        else:
            print( msg, flush=True )
            if not dryrun:
                print( msg, flush=True, file=log_fs )

def is_privileged( log_fs ):
    global error

    if os.environ['USER'] == 'root':
        return True
    able_to_sudo = False
    sudo_rc = sp.call( [ 'sudo',
                         '-S',
                         'true',
                         '<',
                         '/dev/null',
                         '>',
                         '/dev/null/',
                         '2>&1' ] )
    if sudo_rc == 0:
        able_to_sudo = True
    if args.sudo:
        if able_to_sudo:
            sudo_prefix = [ 'sudo', '/bin/sh', '-c' ]
            return True
        else:
            log( [ err_prefix, '--sudo option is required' ], log_fs )
            error = True
    else:
        if able_to_sudo:
            log( [ err_prefix, '$USER is not sudo-able' ], log_fs )
        else:
            log( [ err_prefix, '--sudo option is required and USER is not sudo-able' ],
                 log_fs )
        error = True
    return False

cmd = sys.argv[0]

parser = argparse.ArgumentParser( description='PiP package installing program',
                                  add_help = True )
parser.add_argument( '--how',
                     help    = 'Specifying how to install (yum|docker|spack|github)',
                     type    = str,
                     action  = 'append' )
parser.add_argument( '--version', '-V',
                     help    = 'Specifying PiP version (2 or 3)',
                     type    = str,
                     action  = 'append' )
parser.add_argument( '--prefix', '-p',
                     help    = 'Install directory (spack, github)',
                     type    = str,
                     default = 'install',
                     nargs   = '?' )
parser.add_argument( '--work', '-w',
                     help    = 'Working directory (required in all cases)',
                     type    = str,
                     default = 'work',
                     nargs   = '?' )
parser.add_argument( '--clean', '-c',
                     help    = 'Cleanup working directory when succeeded',
                     action  = 'store_true' )
parser.add_argument( '--sudo', '-s',
                     help    = 'allow sudo (yum, docker)',
                     action  = 'store_true' )
parser.add_argument( '--dryrun', '-d',
                     help    = 'dry run',
                     action  = 'store_true' )
parser.add_argument( '--force', '-f',
                     help    = 'force to delete work directory, if exists',
                     action  = 'store_true' )
parser.add_argument( '--verbose', '-v',
                     help    = 'verbose mode',
                     action  = 'store_true' )
parser.add_argument( '--noglibc',
                     help    = 'Do not build PiP-glibc and PiP_gdb (github)',
                     action  = 'store_true' )
parser.add_argument( '--nogdb',
                     help    = 'Do not build PiP_gdb (github)',
                     action  = 'store_true' )

args = parser.parse_args()

dryrun = args.dryrun

## check how
how_list = set( args.how )
how_allowed = [ 'yum', 'docker', 'spack', 'github', 'git@rccs' ]
if 'all' in how_list:
    flag_multi = True
    how_list = how_allowed
elif how_list == []:
    how_list = [ 'github' ]
else:
    errlist = []
    howlist = []
    for h in how_list:
        if h in how_allowed:
            howlist.append( h )
        else:
            errlist.append( h )
    if errlist != []:
        print( err_prefix, errlist, 'is(are) not acceptable value(s) of --how' )
        parser.print_help()
        sys.exit( 1 )
    if howlist == []:
        parser.print_help()
        sys.exit( 1 )
    how_list = howlist

if len( how_list ) > 1:
    flag_multi = True

## check Linux distribution and version
version = sorted( set( args.version ) )
redhat_ver = redhat_version()
if redhat_ver != 7 and redhat_ver != 8:
    print( err_prefix, 'RHEL', redhat_ver, 'is not supported' )
    sys.exit( 1 )

## Check PiP version
pip_vers = []
if 'ALL' in version:
    if redhat_ver == 7:
        pip_vers = [ 1, 2, 3 ]
    else:
        pip_vers = [ 2, 3 ]
elif 'all' in version:
    pip_vers = [ 2, 3 ]
elif version == []:
    pip_vers = [ 2 ]
else:
    ver_allowed = [ -1, 2, 3 ]
    errlist     = []
    for ver_str in args.version:
        ver = int( ver_str )
        if ver not in ver_allowed:
            errlist.append( ver )
        else:
            pip_vers.append( ver )
    if errlist != []:
        print( err_prefix, errlist, 'is(are) not acceptable value(s) of --version' )
        parser.print_help()
        sys.exit( 1 )

if len( pip_vers ) > 1:
    flag_multi = True

# check arch
arch = cpu_arch()
if arch != 'x86_64' and arch != 'aarch64':
    print( err_prefix, arch, 'is not supported by PiP' )
    sys.exit( 1 )

def make_directory( dir ):
    if not dryrun:
        try:
            os.mkdir( dir )
            return dir
        except Exception as e:
            print( err_prefix, e )
            return None
    else:
        return dir

# check and create prefix dir
def check_prefix( prefix):
    global query_prefix

    prefix = os.path.realpath( os.path.expanduser( prefix ) )
    if dryrun:
        return prefix
    if os.path.isfile( prefix ):
        print( err_prefix, prefix, 'is not a directory' )
        return None
    if os.path.isdir( prefix ):
        print( warn_prefix, 'Prefix directory already exists: ', prefix )
        if not args.force and not query_prefix:
            while True:
                try:
                    choice = input( "Are you sure to install in prefix directory? 'yes' or 'no' [y/N]: ").lower()
                except:
                    print( '' )
                    sys.exit( 1 )

                if choice in [ 'y', 'ye', 'yes' ]:
                    query_prefix = True
                    break
                elif choice in [ 'n', 'no' ]:
                    sys.exit( 1 )
    return prefix

def create_prefix( prefix, how, ver ):
    global flag_multi
    if not flag_multi:
        pdir = prefix
    else:
        pdir = os.path.join( prefix,
                             arch + '_' +
                             'redhat-' + str( redhat_ver ) + '_' +
                             how + '_' +
                             'pip-' + str( ver ) )
    try:
        os.makedirs( pdir, exist_ok=True )
        return pdir
    except Exception as e:
        print( err_prefix, e )
        return None

def delete_work_dir( wdir ):
    print( 'Deleting existing work directory (', wdir, ') ...' )
    try:
        shutil.rmtree( wdir )
    except Exception as e:
        print( err_prefix, e )
        sys.exit( 1 )

# check and create work dir
def check_work( wdir ):
    wdir = os.path.realpath( os.path.expanduser( wdir ) )
    if os.path.isfile( wdir ):
        print( err_prefix, wdir, 'is not a directory' )
        return None, None
    if os.path.isdir( wdir ):
        print( warn_prefix, 'Work directory already exists: ', wdir )
        if not args.force:
            while True:

                try:
                    choice = input( "Delete work directory before install? 'yes' or 'no' [y/N]: ").lower()
                except:
                    print( '' )
                    sys.exit( 1 )

                if choice in ['y', 'ye', 'yes']:
                    break
                elif choice in [ 'n', 'no' ]:
                    sys.exit( 1 )

        delete_work_dir( wdir )
    return wdir

def create_work( work, how, ver ):
    global arch, redhat_ver

    wdir = os.path.join( work,
                         arch + '_' +
                         'redhat-' + str( redhat_ver ) + '_' +
                         how + '_' +
                         'pip-' + str( ver ) )
    try:
        log_dir = os.path.join( wdir, 'log' )
        os.makedirs( log_dir )
        log_file = os.path.join( log_dir, 'pip-pip.log' )
    except Exception as e:
        print( err_prefix, e )
        return None, None
    return wdir, log_file

def check_file( file ):
    if dryrun:
        return True
    return os.path.isfile( file )

def check_command( command ):
    if shutil.which( command  ) == None:
        return False
    return True

def execute( chdir, cmd, log_f, log_fs, tbi ):
    global error

    if dryrun:
        if chdir == None:
            log( [ '[DRY]' ] + cmd + [ '[]' ], log_fs )
        else:
            log( [ '[DRY]' ] + cmd + [ '[' + chdir + ']' ], log_fs )
    elif not tbi:
        if chdir == None:
            log( [ '[TBI]' ] + cmd + [ '[]' ], log_fs )
        else:
            log( [ '[TBI]' ] + cmd + [ '[' + chdir + ']' ], log_fs )
    else:
        ret = -1
        if error:
            log( [ msg_prefix ] + cmd + [ '-- execution skipped due to prev. error' ], log_fs )
            return
        try:
            cmd_redirect = cmd + [ '>>', log_f, '2>&1', '<', '/dev/null' ]
            if chdir == None:
                log( [ msg_prefix ] + cmd + [ '[]' ], log_fs )
                cmd_str = ' '.join( cmd_redirect )
                proc = sp.Popen( [ '/bin/sh', '-c', cmd_str ], close_fds=True )
            else:
                log( [ msg_prefix ] + cmd + [ '[' + chdir + ']' ], log_fs )
                cmd_chdir = [ 'cd', chdir, ';' ] + cmd_redirect
                cmd_str   = ' '.join( cmd_chdir )
                proc = sp.Popen( [ '/bin/sh', '-c', cmd_str ], close_fds=True )

            while True:
                ret = proc.poll()
                if ret is None:
                    print( '.', end='', flush=True )
                    time.sleep( 1 )
                else:
                    if ret == 0:
                        print( ' OK', flush=True )
                    else:
                        print( ' NG', flush=True )
                        error = True
                        return False
                    break
        except Exception as e:
            log( [ 'Exception:', e ], log_fs )
            error = True
            return False
    return True

def install_yum( pip_ver, log_f, log_fs ):
    yum_pip = 'process-in-process-v' + str( pip_ver )
    log( [ msg_enter, 'Yum install', yum_pip ], log_fs )
    if not check_command( 'yum' ):
        log( [ msg_prefix, 'Unable to find YUM' ], log_fs )
        return yum_pip, False
    if not is_privileged( log_fs ):
        return yum_pip, False
    ok = execute( None, sudo_prefix + [ 'yum', 'reinstall', '-y', yum_pip ], log_f, log_fs, False )
    return yum_pip, ok

def install_docker( pip_ver, log_f, log_fs ):
    docker_pip = 'rikenpip/pipv' + str( pip_ver )
    log( [ msg_enter, 'Docker install ', docker_pip ], log_fs )
    if not check_command( 'docker' ):
        log( [ msg_prefix, 'Unable to find DOCKER' ], log_fs )
        return docker_pip, False
    if not is_privileged( log_fs ):
        return docker_pip, False
    if not execute( None,
                    sudo_prefix + [ 'docker', 'inspect', docker_pip ],
                    log_f, log_fs, False ):
        return docker_pip, False
    else:
        log( [ msg_prefix, 'Removing existing image', docker_pip ], log_fs )
        if not execute( None,
                        sudo_prefix + [ 'docker', 'rmi', docker_pip ],
                        log_f, log_fs, False ):
            log( [ err_prefix, 'Failed to remove existing image', coker_pip ], log_fs )
            return docker_pip, False
    log( [ msg_prefix, 'Pulling existing image', docker_pip ], log_fs )
    if execute( None,
                sudo_prefix + [ 'docker', 'pull', docker_pip ],
                log_f, log_fs, False ):
        docker_success = True
        return docker_pip, True
    return docker_pip, False

def install_spack( prefix, how, pip_ver, work_dir, log_f, log_fs ):
    spack_pip = 'process-in-process@', str( pip_ver )
    log( [ msg_enter, 'Spack install', spack_pip ], log_fs )
    if not check_command( 'spack' ):
        if not check_command( 'git' ):
            log( [ err_prefix, 'Unable to find GIT command (required to install Spack)' ], log_fs )
            return spack_pip, False
        else:
            prefix_dir = create_prefix( prefix, how, pip_ver )
            if prefix_dir == None:
                return spack_pip, False
            log( [ msg_prefix, 'Cloning Spack at', prefix_dir ], log_fs )
            if prefix_dir == None:
                return spack_pip, False
            ok = execute( prefix_dir,
                          [ 'git', 'clone', 'https://github.com/spack/spack.git' ],
                          log_f,
                          log_fs,
                          False )
            if not ok:
                return spack_pip, False
            spack_path = os.path.join( prefix_dir, 'spack', 'bin', 'spack' )
    else:
        spack_path = 'spack'
    if execute( None, [ spack_path, 'find', spack_pip ], log_f, log_fs, False ):
        log( [ msg_prefix, 'Uninstalling', spack_pip ], log_fs )
        if not execute( [ spack_path, 'uninstall', spack_pip ], log_f, log_fs, False ):
            return spack_pip, False
    log( [ msg_prefix, 'Installing', spack_pip ], log_fs )
    if execute( None, [ spack_path, 'install', '--test=all',  spack_pip ], log_f, log_fs, False ):
        spack_success = True
        return spack_pip, True
    return spack_pip, False

def install_git( prefix, repo, pip_ver, work_dir, log_f, log_fs  ):
    global redhat_ver

    if repo == 'github':
        git_repo = 'https://github.com/RIKEN-SysSoft'
        pip = 'PiP'
    elif repo == 'git@rccs':
        git_repo = 'git@git.sys.r-ccs.riken.jp:software'
        pip = 'PIP'
    else:
        log( [ err_prefix, 'Unknown git repo:', repo ], log_fs )
        return repo, False
    if not check_command( 'git' ):
        log( [ err_prefix, 'Unable to find GIT command' ], log_fs )
        return git_repo, False

    log( [ msg_enter, 'Git install', git_repo ], log_fs )

    repo_glibc = git_repo + '/' + pip + '-glibc.git'
    repo_pip   = git_repo + '/' + pip + '.git'
    repo_gdb   = git_repo + '/' + pip + '-gdb.git'

    branch_pip = 'pip-' + str( pip_ver )
    if redhat_ver == 7:
        branch_glibc = 'centos/glibc-2.17-260.el7.pip.branch'
        branch_gdb   = 'centos/gdb-7.6.1-94.el7.pip.branch'
    elif redhat_ver == 8:
        branch_glibc = 'centos/glibc-2.28-72.el8_1.1.pip.branch'
        branch_gdb   = 'centos/gdb-7.6.1-94.el7.pip.branch'
    else:
        log( [ msg_error, 'Unsupported Redhat version:', str( redhat_ver ) ], log_fs )
        return git_repo, False

    prefix_dir = create_prefix( prefix, repo, pip_ver )
    if prefix_dir == None:
        return git_repo, False

    glibc_srcdir  = os.path.join( work_dir,     pip + '-glibc' )
    build_script  = os.path.join( glibc_srcdir, 'build.sh' )
    glibc_build   = os.path.join( work_dir,     'glibc_build' )
    glibc_install = os.path.join( prefix_dir,   'glibc_install' )
    if not args.noglibc:
        log( [ msg_prefix, 'Cloning', repo_glibc ], log_fs )
        if not execute( work_dir, [ 'git', 'clone', '-b', branch_glibc, repo_glibc ],
                        log_f, log_fs, True ):
            return git_repo, False

        log( [ msg_prefix, 'Building', repo_glibc ], log_fs )
        if make_directory( glibc_build ) == None:
            return git_repo, False
        if make_directory( glibc_install) == None:
            return git_repo, False
        if not execute( glibc_build,
                        [ build_script, glibc_install ],
                        log_f, log_fs, True ):
            return git_repo, False
        piplnlibs = os.path.join( glibc_install, 'bin', 'piplnlibs.sh' )
        if not check_file( piplnlibs ):
            log( [ msg_error, 'Unable to find: ', piplnlibs ], log_fs )
            return git_repo, False

    log( [ msg_prefix, 'Cloning', repo_pip ], log_fs )
    if not execute( work_dir,
                    [ 'git', 'clone', '-b', branch_pip, repo_pip ],
                    log_f, log_fs, True ):
        return git_repo, False

    log( [ msg_prefix, 'Building', repo_pip ], log_fs )
    pip_dir = os.path.join( work_dir, pip )
    configure = os.path.join( pip_dir, 'configure' )
    if not args.noglibc:
        if not execute( pip_dir,
                        [ configure,
                          '--prefix=' + prefix_dir,
                          '--with-glibc-libdir=' + glibc_install + '/lib' ],
                        log_f, log_fs, True ):
            return git_repo, False
    else:
        if not execute( pip_dir,
                        [ configure,
                          '--prefix=' + prefix_dir ],
                        log_f, log_fs, True ):
            return git_repo, False
    if not execute( pip_dir, [ 'make' ], log_f, log_fs, True ):
        return git_repo, False
    if not execute( pip_dir, [ 'make', 'check' ], log_f, log_fs, True ):
        return git_repo, False
    if not execute( pip_dir, [ 'make', 'install' ], log_f, log_fs, True ):
        return git_repo, False
    if not execute( pip_dir, [ 'make', 'check-installed' ], log_f, log_fs, True ):
        return git_repo, False
    if not execute( pip_dir, [ 'make', 'doc-install' ], log_f, log_fs, True ):
        return git_repo, False
    pipcc = os.path.join( prefix_dir, 'bin', 'pipcc' )
    if not check_file( pipcc ):
        log( [ msg_error, 'Unable to find: ', pipcc ], log_fs )
        return git_repo, False

    if not args.noglibc and not args.nogdb:
        log( [ msg_prefix, 'Cloning', repo_gdb ], log_fs )
        if not execute( work_dir,
                        [ 'git', 'clone', '-b', branch_gdb, repo_gdb ],
                        log_f, log_fs, True ):
            return git_repo, False

        log( [ msg_prefix, 'Building', repo_gdb ], log_fs )
        gdb_dir = os.path.join( work_dir, pip + '-gdb' )
        build_script = os.path.join( gdb_dir, 'build.sh' )
        if not execute( gdb_dir,
                        [ build_script,
                          '--prefix=' + prefix_dir,
                          '--with-pip=' + prefix_dir ],
                        log_f, log_fs, True ):
            return git_repo, False
        pip_gdb = os.path.join( prefix_dir, 'bin', 'pip-gdb' )
        if not check_file( pip_gdb ):
            log( [ msg_error, 'Unable to find: ', pip_gdb ], log_fs )
            return git_repo, False

    return git_repo, True

prefix_dir = check_prefix( args.prefix )
work_dir   = check_work( args.work )

# check work and prefix dirs if work can be deleted
common = os.path.commonpath( [ work_dir, prefix_dir ] )
if common is work_dir:          # this means work_dir is upper of prefix_dir
    if args.clean:
        if not dryrun:
            print( err_prefix, 'Work dir includes prefix dir and work dir cannot be deleted.' )
            sys.exit( 1 )
        else:
            print( warn_prefix, 'Work dir includes prefix dir and work dir cannot be deleted.' )

for how in how_list:
    global error

    last_how= how_list[-1]
    for pip_ver in pip_vers:
        error = False
        last_ver = pip_vers[-1]

        ( wdir, log_file ) = create_work( work_dir, how, pip_ver )
        if log_file == None:
            sys.exit( 1 )

        try:
            with open( log_file, mode='w' ) as log_fs:
                if how == 'yum':
                    ( obj, ok ) = install_yum(    pip_ver, log_file, log_fs )
                elif how == 'docker':
                    ( obj, ok ) = install_docker( pip_ver, log_file, log_fs )
                elif how == 'spack':
                    ( obj, ok ) = install_spack( prefix_dir, how, pip_ver, wdir, log_file, log_fs )
                elif how == 'github':
                    ( obj, ok ) = install_git( prefix_dir,   how, pip_ver, wdir, log_file, log_fs )
                elif how == 'git@rccs':
                    ( obj, ok ) = install_git( prefix_dir,   how, pip_ver, wdir, log_file, log_fs )

                if ok:
                    log( [ msg_exit,  how, 'install', obj, 'OK' ], log_fs )
                else:
                    log( [ msg_error, how, 'install', obj, 'NG' ], log_fs )
                    print( '**** logfile:', log_file, flush=True )

        except Exception as e:
            print( err_prefix, e )
            print( '**** logfile:', log_file, flush=True )

        if not last_ver == pip_ver or not last_how == how:
            print( '' )

if docker_success:
    print( 'To run the PiP Docker image:' )
    print( '  $ [sudo] docker run -it rikenpip/pip-v<PiP-Version> /bin/bash' )

if spack_success and spack_path != '':
    print( 'Spack with PiP was installed at : ', spack_path )
    print( '  $ ', spack_path, ' load ', 'process-in-process[@<PiP-version>]' )

if args.clean and not dryrun:
    delete_work_dir( wdir )

sys.exit( 0 )

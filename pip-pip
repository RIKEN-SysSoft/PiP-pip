#!/usr/bin/env python3

import datetime
import time
import argparse
import shutil
import os
import sys
import subprocess as sp

log_dir     = ''
msg_enter   = '>>>'
msg_exit    = '<<<'
msg_error   = '<ER'
msg_prefix  ='---'
msg_prefix1 ='###'
err_prefix  ='ERROR:'
warn_prefix ='WARNING:'
sep = '\n=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-\n'

sudo_prefix  = []
query_prefix = False
flag_multi   = False
dryrun       = False

def redhat_version():
    with open( '/etc/redhat-release', mode='r' ) as f:
        l = f.readline().split().pop(3).split('.').pop(0)
    return int( l )

def cpu_arch():
    return sp.check_output( [ 'uname', '-m' ] ).decode().split().pop(0)

def log( list, log_fs, newline ):
    last = list[-1]
    for msg in list:
        if msg != last:
            if not args.quiet:
                print( msg, end=' ' )
            if not dryrun:
                print( msg, end=' ', file=log_fs )
        else:
            if newline:
                if not args.quiet:
                    print( msg, flush=True )
                if not dryrun:
                    print( msg, flush=True, file=log_fs )
            else:
                if not args.quiet:
                    print( msg, end='', flush=True )
                if not dryrun:
                    print( msg, end='', flush=True, file=log_fs )

def is_privileged( log_fs ):
    global sudo_query, error

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
            error = True
            if not sudo_query:
                sudo_query = True
                log( [ err_prefix, '--sudo option is required' ], log_fs, True )
    else:
        if not sudo_query:
            sudo_query = True
            if able_to_sudo:
                log( [ err_prefix, 'user is not sudo-able' ], log_fs, True )
            else:
                log( [ err_prefix, '--sudo option is required and user is not sudo-able' ],
                     log_fs, True )
        error = True
    return False

cmd = sys.argv[0]

parser = argparse.ArgumentParser( description='PiP package installing program',
                                  add_help = True )
parser.add_argument( '--how', '-H',
                     help    = 'Specifying how to install (yum|docker|spack|github)',
                     type    = str,
                     action  = 'append' )
parser.add_argument( '--version', '-v',
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
parser.add_argument( '--quiet', '-q',
                     help    = 'quiet mode',
                     action  = 'store_true' )
parser.add_argument( '--noglibc', '-noglibc',
                     help    = 'Do not build PiP-glibc and PiP_gdb (github)',
                     action  = 'store_true' )
parser.add_argument( '--nogdb', '-nogdb',
                     help    = 'Do not build PiP_gdb (github)',
                     action  = 'store_true' )

args = parser.parse_args()

dryrun = args.dryrun

## check how
how_list = set( args.how )
how_allowed = [ 'yum', 'docker', 'spack', 'github', 'git@rccs' ]
if 'all' in how_list or 'ALL' in how_list:
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
            pip_vers.append( abs( ver ) )
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
        if not args.force and not query_prefix:
            if not args.quiet:
                print( warn_prefix, 'Prefix directory already exists: ', prefix )
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
    if not args.quiet:
        if not args.quiet:
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
        if not args.force:
            print( warn_prefix, 'Work directory already exists: ', wdir )
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
        os.makedirs( log_dir, exist_ok=True )
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

def do_poll( proc, dots, tmax, intval, log_fs ):
    delta = 0.2
    t = 0.0
    i = 0

    while True:
        if not args.quiet:
            if t >= i:
                i = i + intval
                print( dots, end='', flush=True )
            elif t > tmax:
                return None
            time.sleep( delta )
            t = t + delta

        ret = proc.poll()
        if ret is None:
            continue
        if ret == 0:
            log( [ ' OK' ], log_fs, True )
            return True
        else:
            log( [ ' NG' ], log_fs, True )
            return False

def execute( chdir, cmd, log_f, log_fs, tbi ):
    global error

    if dryrun:
        if chdir == None:
            log( [ '[DRY]' ] + cmd, log_fs, True )
        else:
            log( [ '[DRY]' ] + cmd, log_fs, True )
    elif not tbi:
        if chdir == None:
            log( [ '[TBI]' ] + cmd, log_fs, True )
        else:
            log( [ '[TBI]' ] + cmd, log_fs, True )
    else:
        ret = -1
        if error:
            log( [ msg_prefix ] + cmd + [ '-- execution skipped due to prev. error' ],
                 log_fs, True )
            error = True
            return False
        try:
            cmd_redirect = cmd + [ '>>', log_f, '2>&1', '<', '/dev/null' ]
            if chdir == None:
                log( [ msg_prefix ] + cmd, log_fs, False )
                cmd_str = ' '.join( cmd_redirect )
            else:
                log( [ msg_prefix ] + cmd, log_fs, False )
                cmd_chdir = [ 'cd', chdir, ';' ] + cmd_redirect
                cmd_str   = ' '.join( cmd_chdir )
            proc = sp.Popen( [ '/bin/sh', '-c', cmd_str ], close_fds=True )

            if not args.quiet:
                print( ' ', end='', flush=True )
            inc = [ ( '.',   10,   1 ),
                    ( '-',   30,   3 ),
                    ( '+',  100,  10 ),
                    ( '=',  300,  30 ) ]
            for ( dot, tmax, inc ) in inc:
                ret = do_poll( proc, dot, tmax, inc, log_fs )
                if ret == None:
                    continue
                elif ret == False:
                    error = True
                    time.sleep( 2 ) # wait for stdout/stderr flushing
                return ret
            while True:
                ret = do_poll( proc, '*', 10000, 100, log_fs )
                if ret == None:
                    continue
                elif ret == False:
                    error = True
                    time.sleep( 2 ) # wait for stdout/stderr flushing
                return ret
        except Exception as e:
            log( [ '\nException:', e ], log_fs, True )
            error = True
            return False

def install_yum( pip_ver, log_f, log_fs ):
    yum_pip = 'process-in-process-v' + str( pip_ver )

    retuple = ( 'yum', yum_pip, '' )
    log( [ msg_enter, 'Yum install', yum_pip ], log_fs, True )

    if not check_command( 'yum' ):
        log( [ err_prefix, 'Unable to find YUM' ], log_fs, True )
        return False, retuple
    if not is_privileged( log_fs ):
        return False, retuple
    if execute( None, sudo_prefix + [ 'yum', 'reinstall', '-y', yum_pip ],
                log_f, log_fs, False ):
        return True, retuple
    return False, retuple

def install_docker( pip_ver, log_f, log_fs ):
    docker_pip = 'rikenpip/pipv' + str( pip_ver )

    retuple = ( 'docker', docker_pip, '' )
    log( [ msg_enter, 'Docker install', docker_pip ], log_fs, True )

    if not check_command( 'docker' ):
        log( [ err_prefix, 'Unable to find DOCKER' ], log_fs, True )
        return False, retuple
    if not is_privileged( log_fs ):
        return False, ( 'docker', docker_pip, '' )
    if not execute( None,
                    sudo_prefix + [ 'docker', 'inspect', docker_pip ],
                    log_f, log_fs, False ):
        return False, retuple
    log( [ msg_prefix1, 'Removing existing image', docker_pip ], log_fs, True )
    if not execute( None,
                    sudo_prefix + [ 'docker', 'rmi', docker_pip ],
                    log_f, log_fs, False ):
        log( [ err_prefix, 'Failed to remove existing image', coker_pip ],
             log_fs, True )
        return False, retuple
    log( [ msg_prefix1, 'Pulling existing image', docker_pip ], log_fs, True )
    if execute( None,
                sudo_prefix + [ 'docker', 'pull', docker_pip ],
                log_f, log_fs, False ):
        return True, retuple
    return False, retuple

def install_spack( prefix, how, pip_ver, work_dir, log_f, log_fs ):
    spack_pip = 'process-in-process@', str( pip_ver )

    retuple = ( 'spack', spack_pip, '' )
    log( [ msg_enter, 'Spack install', spack_pip ], log_fs, True )

    if not check_command( 'spack' ):
        if not check_command( 'git' ):
            log( [ err_prefix, 'Unable to find GIT command (required to install Spack)' ],
                 log_fs, True )
            return False, retuple
        prefix_dir = create_prefix( prefix, how, pip_ver )
        if prefix_dir == None:
            return False, retuple
        log( [ msg_prefix1, 'Cloning Spack at', prefix_dir ], log_fs, True )
        if not execute( prefix_dir,
                        [ 'git', 'clone', 'https://github.com/spack/spack.git' ],
                        log_f,
                        log_fs,
                        False ):
            return False, retuple
        spack_path = os.path.join( prefix_dir, 'spack', 'bin', 'spack' )
    else:
        spack_path = 'spack'

    retuple = ( 'spack', spack_pip, spack_path )
    if execute( None, [ spack_path, 'find', spack_pip ], log_f, log_fs, False ):
        log( [ msg_prefix1, 'Uninstalling', spack_pip ], log_fs, True )
        if not execute( [ spack_path, 'uninstall', spack_pip ], log_f, log_fs, False ):
            return False, retuple
    log( [ msg_prefix1, 'Installing', spack_pip ], log_fs, True )
    if execute( None, [ spack_path, 'install', '--test=all',  spack_pip ], log_f, log_fs, False ):
        return True, retuple
    return False, retuple

def install_git( prefix, repo, pip_ver, work_dir, log_f, log_fs  ):
    global redhat_ver

    branch_pip = 'pip-' + str( pip_ver )

    retuple = ( 'git', repo + '@' + branch_pip, '' )
    if repo == 'github':
        git_repo = 'https://github.com/RIKEN-SysSoft'
        pip = 'PiP'
    elif repo == 'git@rccs':
        git_repo = 'git@git.sys.r-ccs.riken.jp:software'
        pip = 'PIP'
    else:
        log( [ err_prefix, 'Unknown git repo:', repo ], log_fs, True )
        return False, retuple
    if not check_command( 'git' ):
        log( [ err_prefix, 'Unable to find GIT command' ], log_fs, True )
        return False, retuple

    log( [ msg_enter, 'Git install', git_repo, 'PiP-v'+str( pip_ver ) ], log_fs, True )

    repo_glibc = git_repo + '/' + pip + '-glibc.git'
    repo_pip   = git_repo + '/' + pip + '.git'
    repo_gdb   = git_repo + '/' + pip + '-gdb.git'

    git_pip = repo_pip + '@' + branch_pip
    retuple = ( 'git', git_pip, '' )
    if redhat_ver == 7:
        branch_glibc = 'centos/glibc-2.17-260.el7.pip.branch'
        branch_gdb   = 'centos/gdb-7.6.1-94.el7.pip.branch'
    elif redhat_ver == 8:
        branch_glibc = 'centos/glibc-2.28-72.el8_1.1.pip.branch'
        branch_gdb   = 'centos/gdb-7.6.1-94.el7.pip.branch'
    else:
        log( [ msg_error, 'Unsupported Redhat version:', str( redhat_ver ) ],
             log_fs, True )
        return False, retuple

    prefix_dir = create_prefix( prefix, repo, pip_ver )
    if prefix_dir == None:
        return False, retuple
    retuple = ( 'git', git_pip, prefix_dir )

    glibc_srcdir  = os.path.join( work_dir,     pip + '-glibc' )
    build_script  = os.path.join( glibc_srcdir, 'build.sh' )
    glibc_build   = os.path.join( work_dir,     'glibc_build' )
    glibc_install = os.path.join( prefix_dir,   'glibc_install' )
    if args.noglibc:
        log( [ msg_prefix1, 'Skipping PiP-glibc build (--noglibc)' ], log_fs, True )
    else:
        log( [ msg_prefix1, 'Cloning', repo_glibc ], log_fs, True )
        if not execute( work_dir, [ 'git', 'clone', '-b', branch_glibc, repo_glibc ],
                        log_f, log_fs, True ):
            return False, retuple
        log( [ msg_prefix1, 'Building', repo_glibc ], log_fs, True )
        if make_directory( glibc_build ) == None:
            return False, retuple
        if make_directory( glibc_install) == None:
            return False, retuple
        if not execute( glibc_build,
                        [ build_script, glibc_install ],
                        log_f, log_fs, True ):
            return False, retuple
        piplnlibs = os.path.join( glibc_install, 'bin', 'piplnlibs.sh' )
        if not check_file( piplnlibs ):
            log( [ msg_error, 'Unable to find: ', piplnlibs ], log_fs, True )
            return False, retuple

    log( [ msg_prefix1, 'Cloning', repo_pip ], log_fs, True )
    if not execute( work_dir,
                    [ 'git', 'clone', '-b', branch_pip, repo_pip ],
                    log_f, log_fs, True ):
        return False, retuple

    log( [ msg_prefix1, 'Building', repo_pip ], log_fs, True )
    pip_dir = os.path.join( work_dir, pip )
    configure = os.path.join( pip_dir, 'configure' )
    if args.noglibc:
        if not execute( pip_dir,
                        [ configure,
                          '--prefix=' + prefix_dir ],
                        log_f, log_fs, True ):
            return False, retuple
    else:
        if not execute( pip_dir,
                        [ configure,
                          '--prefix=' + prefix_dir,
                          '--with-glibc-libdir=' + glibc_install + '/lib' ],
                        log_f, log_fs, True ):
            return False, retuple
    if not execute( pip_dir, [ 'make' ], log_f, log_fs, True ):
        return False, retuple
    if not execute( pip_dir, [ 'make', 'check' ], log_f, log_fs, True ):
        return False, retuple
    if not execute( pip_dir, [ 'make', 'install' ], log_f, log_fs, True ):
        return False, retuple
    if not execute( pip_dir, [ 'make', 'check-installed' ], log_f, log_fs, True ):
        return False, retuple
    if not execute( pip_dir, [ 'make', 'doc-install' ], log_f, log_fs, True ):
        return False, retuple
    pipcc = os.path.join( prefix_dir, 'bin', 'pipcc' )
    if not check_file( pipcc ):
        log( [ msg_error, 'Unable to find: ', pipcc ], log_fs, True )
        return False, retuple

    if args.noglibc or args.nogdb:
        log( [ msg_prefix1, 'Skipping PiP-gdb build (--noglibc or --nogdb)' ], log_fs, True )
    else:
        log( [ msg_prefix1, 'Cloning', repo_gdb ], log_fs, True )
        if not execute( work_dir,
                        [ 'git', 'clone', '-b', branch_gdb, repo_gdb ],
                        log_f, log_fs, True ):
            return False, retuple

        log( [ msg_prefix1, 'Building', repo_gdb ], log_fs, True )
        gdb_dir = os.path.join( work_dir, pip + '-gdb' )
        build_script = os.path.join( gdb_dir, 'build.sh' )
        if not execute( gdb_dir,
                        [ build_script,
                          '--prefix=' + prefix_dir,
                          '--with-pip=' + prefix_dir ],
                        log_f, log_fs, True ):
            return False, retuple
        pip_gdb = os.path.join( prefix_dir, 'bin', 'pip-gdb' )
        if not check_file( pip_gdb ):
            log( [ msg_error, 'Unable to find: ', pip_gdb ], log_fs, True )
            return False, retuple
    return True, retuple

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

list_success = []
list_failure = []

for h in how_list:
    last_how = how_list[-1]
    for pip_ver in pip_vers:
        sudo_query = False
        error      = False
        last_ver = pip_vers[-1]

        ( wdir, log_file ) = create_work( work_dir, h, pip_ver )
        if log_file == None:
            sys.exit( 1 )

        try:
            with open( log_file, mode='w', encoding='utf-8' ) as log_fs:
                now_str = datetime.datetime.now().strftime( '%Y-%m-%d %H:%M:%S' )
                print( now_str, sep, file=log_fs )

                if h == 'yum':
                    retuple = install_yum(    pip_ver, log_file, log_fs )
                elif h == 'docker':
                    retuple = install_docker( pip_ver, log_file, log_fs )
                elif h == 'spack':
                    retuple = install_spack( prefix_dir, h, pip_ver, wdir, log_file, log_fs )
                elif h == 'github':
                    retuple = install_git( prefix_dir,   h, pip_ver, wdir, log_file, log_fs )
                elif h == 'git@rccs':
                    retuple = install_git( prefix_dir,   h, pip_ver, wdir, log_file, log_fs )

                ( ok, ( how, obj, note ) ) = retuple
                if ok:
                    list_success.append( ( how, obj, note ) )
                    log( [ msg_exit,  h, 'install', obj, 'OK' ], log_fs, True )
                else:
                    list_failure.append( ( how, obj, log_file ) )
                    log( [ msg_error, h, 'install', obj, 'NG' ], log_fs, True )

                now_str = datetime.datetime.now().strftime( '%Y-%m-%d %H:%M:%S' )
                print( sep, now_str, file=log_fs )

        except Exception as e:
            print( err_prefix, e )
            print( '**** logfile:', log_file, flush=True )
        except KeyboardInterrupt:
            print( '\n^C' )
            sys.exit( 1 )

        if not last_ver == pip_ver or not last_how == h:
            if not args.quiet:
                print( '' )

if args.clean and not dryrun:
    if list_failure == []:
        delete_work_dir( wdir )
    elif not args.quiet:
        print( '--clean is disabled due to the error' )

if not args.quiet:
    docker_success = False

    print( '\nSummary' )
    if list_success != []:
        for ( how, obj, note ) in list_success:
            if how == 'docker':
                docker_success = True
            print( 'OK  ', end='' )
            if note == '':
                print( how, '  ', obj )
            else:
                print( how, '  ', obj, '  ', note )

    if docker_success:
        print( 'To run the PiP Docker image:' )
        print( '  $ [sudo] docker run -it rikenpip/pip-v<PiP-Version> /bin/bash' )

    if list_failure != []:
        for ( how, obj, log_file ) in list_failure:
            print( 'NG  ', end='' )
            if log_file == '':
                print( how, '  ', obj )
            else:
                print( how, '  ', obj, '  LOG:' + log_file )

if list_failure != []:
    sys.exit( 1 )

sys.exit( 0 )

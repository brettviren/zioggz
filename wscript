VERSION='0.0.0'
APPNAME='ziogg'

top = '.'
out = 'build'

def options(opt):
    opt.load('compiler_cxx')
    opt.load('waf_unit_test')

def configure(cfg):
    cfg.env.CXXFLAGS += ['-std=c++17', '-g', '-O2']
    cfg.load('compiler_cxx')
    cfg.load('waf_unit_test')
    p = dict(mandatory=True, args='--cflags --libs')
    cfg.check_cfg(package='libzmq', uselib_store='ZMQ', **p);
    cfg.check_cfg(package='libczmq', uselib_store='CZMQ', **p);
    cfg.check_cfg(package='libzyre', uselib_store='ZYRE', **p);
    cfg.check_cfg(package='oggz', uselib_store='OGGZ', **p);
    cfg.check_cfg(package='libzio', uselib_store='ZIO', **p);
    cfg.write_config_header('config.h')


def build(bld):
    uses='ZMQ CZMQ ZYRE ZIO'.split()

    rpath = [bld.env["PREFIX"] + '/lib', bld.path.find_or_declare(bld.out_dir)]
    rpath += [bld.env["LIBPATH_%s"%u][0] for u in uses]
    rpath = list(set(rpath))
    print ('\n'.join([str(p) for p in rpath]))
             
    sources = bld.path.ant_glob('src/*.cpp');
    bld.shlib(features='cxx', includes='inc', rpath=rpath,
              source = sources, target='ziogg',
              uselib_store='ZIOGG', use=uses)

    tsources = bld.path.ant_glob('test/test*.cpp')
    for tmain in tsources:
        bld.program(features = 'test cxx',
                    source = [tmain], target = tmain.name.replace('.cpp',''),
                    ut_cwd = bld.path, install_path = None,
                    includes = ['inc','build','test'],
                    rpath = rpath,
                    use = ['ziogg'] + uses)

    bld.install_files('${PREFIX}/include/ziogg', bld.path.ant_glob("inc/ziogg/*.hpp"))

    # fake pkg-config
    bld(source='libziogg.pc.in', VERSION=VERSION,
        LLIBS='-lziogg', REQUIRES='libczmq libzmq libzyre libzio oggz')
    # fake libtool
    bld(features='subst',
        source='libziogg.la.in', target='libziogg.la',
        **bld.env)
    bld.install_files('${PREFIX}/lib', bld.path.find_or_declare("libziogg.la"))
    
    from waflib.Tools import waf_unit_test
    bld.add_post_fun(waf_unit_test.summary)

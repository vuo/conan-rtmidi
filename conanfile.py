from conans import ConanFile, CMake, tools
import platform

class RtMidiConan(ConanFile):
    name = 'rtmidi'

    source_version = '4.0.0'
    package_version = '1'
    version = '%s-%s' % (source_version, package_version)

    build_requires = (
        'llvm/5.0.2-1@vuo/stable',
        'macos-sdk/11.0-0@vuo/stable',
        'vuoutils/1.2@vuo/stable',
    )
    settings = 'os', 'compiler', 'build_type', 'arch'
    url = 'http://www.music.mcgill.ca/~gary/rtmidi/'
    license = 'http://www.music.mcgill.ca/~gary/rtmidi/#license'
    description = 'A cross-platform library for realtime MIDI input/output'
    generators = 'cmake'
    source_dir = 'rtmidi-%s' % source_version
    exports_sources = '*.patch'

    build_dir = '_build'
    install_dir = '_install'

    libs = {
        'rtmidi': 5,
    }

    def requirements(self):
        if platform.system() == 'Linux':
            self.requires('patchelf/0.10pre-1@vuo/stable')
        elif platform.system() != 'Darwin':
            raise Exception('Unknown platform "%s"' % platform.system())

    def source(self):
        tools.get('http://www.music.mcgill.ca/~gary/rtmidi/release/rtmidi-%s.tar.gz' % self.source_version,
                  sha256='370cfe710f43fbeba8d2b8c8bc310f314338c519c2cf2865e2d2737b251526cd')

        # README.md contains the license at the end.
        self.run('sed -n \'/The RtMidi license/,$p\' %s/README.md > %s/%s.txt' % (self.source_dir, self.source_dir, self.name))

    def build(self):
        cmake = CMake(self)
        cmake.definitions['CMAKE_BUILD_TYPE'] = 'Release'
        cmake.definitions['CMAKE_C_COMPILER'] = self.deps_cpp_info['llvm'].rootpath + '/bin/clang'
        cmake.definitions['CMAKE_C_FLAGS'] = '-Oz -DNDEBUG'
        cmake.definitions['CMAKE_OSX_ARCHITECTURES'] = 'x86_64;arm64'
        cmake.definitions['CMAKE_OSX_DEPLOYMENT_TARGET'] = '10.11'
        cmake.definitions['CMAKE_OSX_SYSROOT'] = self.deps_cpp_info['macos-sdk'].rootpath
        cmake.definitions['CMAKE_INSTALL_PREFIX'] = '../%s' % self.install_dir
        cmake.definitions['CMAKE_SHARED_LINKER_FLAGS'] = '-Wl,-macos_version_min,10.11'
        cmake.definitions['RTMIDI_API_JACK'] = False

        tools.mkdir(self.build_dir)
        with tools.chdir(self.build_dir):
            cmake.configure(source_dir='../%s' % self.source_dir,
                            build_dir='.')
            cmake.build()
            cmake.install()

        import VuoUtils
        with tools.chdir('%s/lib' % self.install_dir):
            VuoUtils.fixLibs(self.libs, self.deps_cpp_info)

    def package(self):
        if platform.system() == 'Darwin':
            libext = 'dylib'
        elif platform.system() == 'Linux':
            libext = 'so'

        self.copy('*.h', src='%s/include' % self.install_dir, dst='include/RtMidi')
        self.copy('librtmidi.%s' % libext, src='%s/lib' % self.install_dir, dst='lib')

        self.copy('%s.txt' % self.name, src=self.source_dir, dst='license')

    def package_info(self):
        self.cpp_info.libs = ['rtmidi']

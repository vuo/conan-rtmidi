from conans import AutoToolsBuildEnvironment, ConanFile, tools
import platform

class RtMidiConan(ConanFile):
    name = 'rtmidi'

    source_version = '2.0.1'
    package_version = '2'
    version = '%s-%s' % (source_version, package_version)

    requires = 'llvm/3.3-2@vuo/stable', \
               'vuoutils/1.0@vuo/stable'
    settings = 'os', 'compiler', 'build_type', 'arch'
    url = 'http://www.music.mcgill.ca/~gary/rtmidi/'
    license = 'http://www.music.mcgill.ca/~gary/rtmidi/#license'
    description = 'A cross-platform library for realtime MIDI input/output'
    source_dir = 'rtmidi-%s' % source_version
    exports_sources = '*.patch'
    libs = {
        'rtmidi': 2,
    }

    def requirements(self):
        if platform.system() == 'Linux':
            self.requires('patchelf/0.10pre-1@vuo/stable')
        elif platform.system() != 'Darwin':
            raise Exception('Unknown platform "%s"' % platform.system())

    def source(self):
        tools.get('http://www.music.mcgill.ca/~gary/rtmidi/release/rtmidi-%s.tar.gz' % self.source_version,
                  sha256='b5017a91df0c2bc4c0d5c6548ac5f9696c5bc0c202f6bec704563c6f6bec64ec')

        tools.patch(patch_file='disable-static.patch', base_path=self.source_dir)

        self.run('mv %s/readme %s/%s.txt' % (self.source_dir, self.source_dir, self.name))

    def build(self):
        import VuoUtils
        # RtMIDI doesn't support shadow builds, so build in source_dir.
        with tools.chdir(self.source_dir):
            autotools = AutoToolsBuildEnvironment(self)

            # The LLVM/Clang libs get automatically added by the `requires` line,
            # but this package doesn't need to link with them.
            autotools.libs = []

            env_vars = {
                'CC' : self.deps_cpp_info['llvm'].rootpath + '/bin/clang',
                'CXX': self.deps_cpp_info['llvm'].rootpath + '/bin/clang++',
            }
            with tools.environment_append(env_vars):
                autotools.configure(build=False,
                                    host=False,
                                    args=['--quiet',
                                          '--enable-shared'])
                autotools.make(args=['--quiet'])

            VuoUtils.fixLibs(self.libs, self.deps_cpp_info)

    def package(self):
        if platform.system() == 'Darwin':
            libext = 'dylib'
        elif platform.system() == 'Linux':
            libext = 'so'

        self.copy('*.h', src=self.source_dir, dst='include/RtMidi')
        self.copy('librtmidi.%s' % libext, src=self.source_dir, dst='lib')

        self.copy('%s.txt' % self.name, src=self.source_dir, dst='license')

    def package_info(self):
        self.cpp_info.libs = ['rtmidi']

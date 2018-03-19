from conans import AutoToolsBuildEnvironment, ConanFile, tools

class RtMidiConan(ConanFile):
    name = 'rtmidi'

    source_version = '2.0.1'
    package_version = '1'
    version = '%s-%s' % (source_version, package_version)

    requires = 'llvm/3.3-1@vuo/stable',
    settings = 'os', 'compiler', 'build_type', 'arch'
    url = 'http://www.music.mcgill.ca/~gary/rtmidi/'
    license = 'http://www.music.mcgill.ca/~gary/rtmidi/#license'
    description = 'A cross-platform library for realtime MIDI input/output'
    source_dir = 'rtmidi-%s' % source_version

    def source(self):
        tools.get('http://www.music.mcgill.ca/~gary/rtmidi/release/rtmidi-%s.tar.gz' % self.source_version,
                  sha256='b5017a91df0c2bc4c0d5c6548ac5f9696c5bc0c202f6bec704563c6f6bec64ec')

    def build(self):
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

            self.run('install_name_tool -id @rpath/librtmidi.dylib librtmidi.dylib')

    def package(self):
        self.copy('*.h', src=self.source_dir, dst='include/RtMidi')
        self.copy('librtmidi.dylib', src=self.source_dir, dst='lib')

    def package_info(self):
        self.cpp_info.libs = ['rtmidi']

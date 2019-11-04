from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
import os


def sort_libs(correct_order, libs, lib_suffix='', reverse_result=False):
    # Add suffix for correct string matching
    correct_order[:] = [s.__add__(lib_suffix) for s in correct_order]

    result = []
    for expectedLib in correct_order:
        for lib in libs:
            if expectedLib == lib:
                result.append(lib)

    if reverse_result:
        # Linking happens in reversed order
        result.reverse()

    return result


class CorradeConan(ConanFile):
    name = "corrade"
    description = "Corrade is a multiplatform utility library written in C++11/C++14."
    topics = ("conan", "corrade", "magnum", "filesystem", "console", "environment", "os")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://magnum.graphics/corrade"
    license = "MIT"
    exports_sources = ["CMakeLists.txt"]
    generators = "cmake"
    short_paths = True

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "build_deprecated": [True, False],
        "with_interconnect": [True, False],
        "with_pluginmanager": [True, False],
        "with_testsuite": [True, False],
        "with_utility": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "build_deprecated": True,
        "with_interconnect": True,
        "with_pluginmanager": True,
        "with_testsuite": True,
        "with_utility": True,
    }

    _source_subfolder = "source_subfolder"
    _build_subfolder = "build_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.settings.compiler == "Visual Studio" and tools.Version(self.settings.compiler.version.value) < 14:
            raise ConanInvalidConfiguration("Corrade requires Visual Studio version 14 or greater")
        if tools.cross_building(self.settings):
             raise ConanInvalidConfiguration("This Corrade recipe doesn't support cross building yet")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["BUILD_STATIC"] = "ON" if not self.options.shared else "OFF"
        cmake.definitions["BUILD_DEPRECARED"] = "ON" if not self.options["build_deprecated"] else "OFF"
        cmake.definitions["WITH_INTERCONNECT"] = "ON" if not self.options["with_interconnect"] else "OFF"
        cmake.definitions["WITH_PLUGINMANAGER"] = "ON" if not self.options["with_pluginmanager"] else "OFF"
        cmake.definitions["WITH_TESTSUITE"] = "ON" if not self.options["with_testsuite"] else "OFF"
        cmake.definitions["WITH_UTILITY"] = "ON" if not self.options["with_utility"] else "OFF"

        cmake.definitions["WITH_RC"] = "OFF"  # This executable goes to its own package corrade-rc

        # Corrade uses suffix on the resulting 'lib'-folder when running cmake.install()
        # Set it explicitly to empty, else Corrade might set it implicitly (eg. to "64")
        cmake.definitions["LIB_SUFFIX"] = ""

        if self.settings.compiler == "Visual Studio":
            cmake.definitions["MSVC2015_COMPATIBILITY"] = "ON" if tools.Version(self.settings.compiler.version.value) == 14 else "OFF"
            cmake.definitions["MSVC2017_COMPATIBILITY"] = "ON" if tools.Version(self.settings.compiler.version.value) == 14 else "OFF"

        cmake.configure(build_folder=self._build_subfolder)

        return cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("COPYING", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, 'share')) # does only contain .cmake files

    def package_info(self):
        # See dependency order here: https://doc.magnum.graphics/magnum/custom-buildsystems.html
        allLibs = [
            #1
            "CorradeUtility",
            "CorradeContainers",
            #2
            "CorradeInterconnect",
            "CorradePluginManager",
            "CorradeTestSuite",
        ]

        # Sort all built libs according to above, and reverse result for correct link order
        suffix = '-d' if self.settings.build_type == "Debug" else ''
        builtLibs = tools.collect_libs(self)
        self.cpp_info.libs = sort_libs(correct_order=allLibs, libs=builtLibs, lib_suffix=suffix, reverse_result=True)

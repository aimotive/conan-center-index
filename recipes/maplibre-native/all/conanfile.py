from conan import ConanFile
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.scm import Git
from conan.tools.files import apply_conandata_patches, export_conandata_patches, copy
import subprocess as sp
from pathlib import Path


class MaplibreNativeConan(ConanFile):
    name = "maplibre-native"
    description = "MapLibre GL Native is a community led fork derived from mapbox-gl-native prior to their switch to a non-OSS license"
    license = "BSD2"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://git.aimotive.com/david.bucsu/maplibre-gl-native"
    topics = ("map", "rendering", "opengl-es")
    package_type = "library"
    settings = "os", "arch", "build_type", "compiler"

    requires = "libcurl/[>=8.0 <9]", "glfw/3.4", "libuv/1.49.2", "libjpeg/9f", "libpng/[>=1.6 <2]"
    options = {"shared": [True, False],
               "fPIC": [True, False]}

    default_options = {"shared": False,
                       "fPIC": True}

    def export_sources(self):
        export_conandata_patches(self)

    def layout(self):
        cmake_layout(self, src_folder="src")

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["MBGL_WITH_QT"] = False
        tc.variables["MBGL_WITH_OPENGL"] = False
        tc.variables["MBGL_WITH_EGL"] = True
        tc.variables["MBGL_USE_GLES2"] = True
        tc.variables["MBGL_WITH_RTTI"] = True
        tc.variables["MBGL_WITH_CORE_ONLY"] = False
        tc.variables["CMAKE_FIND_PACKAGE_PREFER_CONFIG"] = True
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def source(self):
        git = Git(self)
        git.clone(url="ssh://git@git.aimotive.com:29418/david.bucsu/maplibre-gl-native.git", target=".")
        git.folder = self.folders.source
        git.checkout("9e90b9e0b63334b03de2186bda98442e2fec25b4")
        git.run("submodule update --init --recursive")

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE.*", src=self.source_folder, dst=Path(self.package_folder, "licenses"))
        copy(self, "*.a", src=self.build_folder, dst=Path(self.package_folder, "lib"))
        sp.check_call(args=["python3", f"{self.source_folder}/scripts/gather_includes.py", "-b", str(self.source_folder), "-i", str(self.source_folder), str(Path(self.source_folder, "platform/default")), "-o", str(Path(self.package_folder, "include")), "-f"])

    def package_info(self):
        self.cpp_info.libdirs = [ "lib", "lib/platform/glfw" ]
        self.cpp_info.libs = [ "mbgl-core", "mbgl-vendor-csscolorparser", "mbgl-vendor-icu", "mbgl-vendor-nunicode", "mbgl-vendor-parsedate", "mbgl-vendor-sqlite", "mbgl-glfw" ]
        self.cpp_info.set_property("cmake_target_name", "Maplibre::Maplibre")
        self.cpp_info.set_property("cmake_file_name", "Maplibre")

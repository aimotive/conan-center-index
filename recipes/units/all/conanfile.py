from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.files import copy, get, rmdir, export_conandata_patches, apply_conandata_patches
from conan.tools.scm import Version
from conan.tools.cmake import CMake
from conan.tools.cmake.layout import cmake_layout
import os

required_conan_version = ">=1.50.0"


class UnitsConan(ConanFile):
    name = "units"
    description = (
        "A compile-time, dimensional analysis and unit conversion "
        "library built on c++14 with no dependencies"
    )
    license = "MIT"
    topics = ("unit-conversion", "dimensional-analysis", "cpp14",
              "template-metaprogramming", "compile-time", "no-dependencies")
    homepage = "https://github.com/nholthaus/units"
    url = "https://github.com/conan-io/conan-center-index"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True
    generators = "CMakeToolchain"


    @property
    def _min_cppstd(self):
        return "14"

    @property
    def _minimum_compilers_version(self):
        return {
            "clang": "3.4",
            "gcc": "4.9.3",
            "Visual Studio": "14",
            "msvc": "190",
        }

    def layout(self):
        cmake_layout(self, src_folder="src")

    def package_id(self):
        self.info.clear()

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._min_cppstd)
        minimum_version = self._minimum_compilers_version.get(str(self.settings.compiler), False)
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support.",
            )

    def export_sources(self):
        export_conandata_patches(self)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        if "aimotive" in self.version:
            apply_conandata_patches(self)

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "units")
        self.cpp_info.set_property("cmake_target_name", "units::units")
        self.cpp_info.libs = ["units"]
        self.cpp_info.includedirs = ["include", "include/units"]

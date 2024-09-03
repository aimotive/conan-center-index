from conan import ConanFile
from conan.tools.files import copy, get
from conan.tools.cmake.layout import cmake_layout
import os

required_conan_version = ">=1.50.0"

class EggsVariantConan(ConanFile):
    name = "eggs.variant"
    homepage = "https://github.com/eggs-cpp/variant"
    description = "eggs.variant - A C++17-like variant, a type-safe union for C++98, C++11 and later in a single-file header-only library"
    topics = ("cpp98", "cpp11", "cpp14", "cpp17", "variant", "variant-implementations")
    license = "BSL-1.0"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    def layout(self):
        cmake_layout(self, src_folder="src")

    def package_id(self):
        self.info.clear()

    def source(self):
        get(self, **self.conan_data["sources"][self.version], destination=self.source_folder, strip_root=True)

    def build(self):
        pass

    def package(self):
        copy(self, "*.hpp", src=os.path.join(self.source_folder, "include"), dst=os.path.join(self.package_folder, "include"))
        copy(self, "LICENSE.txt", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "eggs.variant")
        self.cpp_info.set_property("cmake_target_name", "Eggs::Variant")
        self.cpp_info.bindirs = []
        self.cpp_info.frameworkdirs = []
        self.cpp_info.libdirs = []
        self.cpp_info.resdirs = []
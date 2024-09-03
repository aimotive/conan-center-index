from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import get, replace_in_file
import os
import json

class IoncConan(ConanFile):
    name = "ion-c"
    version = "1.0.6"
    license = "Apache"
    url = "https://github.com/amzn/ion-c"
    description = "A C implementation of the Ion data notation."
    topics = ("amazon ion", "serialization")
    settings = "os", "compiler", "build_type", "arch"
    generators = "CMakeDeps", "CMakeToolchain"

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], destination=self.source_folder, strip_root=True)
        replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"), "add_subdirectory(test)", "# add_subdirectory(test)")
        replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"), "add_subdirectory(tools)", "# add_subdirectory(tools)")

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "IonC"
        self.cpp_info.names["cmake_find_package_multi"] = "IonC"
        self.cpp_info.set_property("cmake_file_name", "IonC")
        self.cpp_info.components["ionc"].set_property("cmake_target_name", "IonC::ionc")
        self.cpp_info.components["ionc"].libs = ["ionc"]
        self.cpp_info.components["ionc"].requires = ["decNumber"]

        self.cpp_info.components["decNumber"].set_property("cmake_target_name", "IonC::decNumber")
        self.cpp_info.components["decNumber"].libs = ["decNumber"]

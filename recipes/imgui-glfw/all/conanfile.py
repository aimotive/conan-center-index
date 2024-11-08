from conan import ConanFile
from conan.tools.cmake.layout import cmake_layout
from conan.tools.cmake import CMakeToolchain, CMake
from conan.tools.files import get, apply_conandata_patches, copy, rmdir
import os

class ImguiConan(ConanFile):
    name = "imgui-glfw"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/aimotive-legacy/imgui-glfw"
    description = "Bloat-free Immediate Mode Graphical User interface for C++ with minimal dependencies (with Aimotive's mods)"
    topics = "gui", "graphical", "bloat-free", "aimotive"
    license = "MIT"

    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}
    requires = "glm/[<1.0]"
    generators = "CMakeDeps"

    def requirements(self):
        if self.settings.os is not "Android":
            self.requires("glfw/[>=3.3.8 <4.0]")

    def export_sources(self):
        for p in self.conan_data.get("patches", {}).get(self.version, []):
            copy(self, p["patch_file"], self.recipe_folder, self.export_sources_folder)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def generate(self):
        tc = CMakeToolchain(self)
        tc.generate()

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "examples"))
        rmdir(self, os.path.join(self.package_folder, "bin"))

    def package_info(self):
        self.cpp_info.libs = ["imgui"]
        self.cpp_info.set_property("cmake_file_name", "imgui")
        self.cpp_info.set_property("cmake_target_name", "imgui::imgui-glfw")

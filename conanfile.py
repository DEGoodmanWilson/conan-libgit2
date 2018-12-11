#!/usr/bin/env python
# -*- coding: utf-8 -*-

from conans import ConanFile, CMake, tools
from shutil import copy2
import os


class Libgit2Conan(ConanFile):
    name = "libgit2"
    version = "0.26.0"
    url = "https://github.com/impsnldavid/conan-libgit2"
    description = "A portable, pure C implementation of the Git core methods"
    license = "GPLv2 with Linking Exception"
    exports = ["LICENSE.md"]
    exports_sources = ["CMakeLists.txt", "FindLIBSSH2.cmake" ]
    generators = "cmake"

    requires = "zlib/1.2.8@conan/stable", "libcurl/7.61.1@bincrafters/stable", "libiconv/1.15@bincrafters/stable"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "threadsafe": [True, False],
        "use_sha1dc": [True, False],
        "use_iconv": [True, False],
        "with_openssl": [True, False],
        "with_ssh": [True, False],
        "use_winhttp": [True, False]
    }
    default_options = (
        "shared=False",
        "threadsafe=True",
        "use_sha1dc=False",
        "use_iconv=False",
        "with_openssl=True",
        "with_ssh=True",
        "use_winhttp=True"
    )

    source_subfolder = "source_subfolder"
    build_subfolder = "build_subfolder"

    def source(self):
        source_url = "https://github.com/libgit2/libgit2"
        tools.get("{0}/archive/v{1}.tar.gz".format(source_url, self.version))
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self.source_subfolder)

    def requirements(self):
        if self.options.with_openssl and (tools.os_info.is_macos or (self.settings.os == "Windows" and self.options.use_winhttp)):
        	self.options.with_openssl = False

        if self.options.with_openssl:
            self.options["libcurl"].with_openssl = True
        else:
            self.options["libcurl"].with_openssl = False

        # if self.options.with_ssh:
        #     self.options["libcurl"].with_libssh2 = True
        # else:
        #     self.options["libcurl"].with_libssh2 = False

        if tools.os_info.is_macos:
            if "libcurl" in self.requires:
                del self.requires["libcurl"]

    def build(self):

        # On Windows we need to replace part of the original CMakeLists file in order to locate libssh2
        if not tools.os_info.is_macos:
            tools.replace_in_file(self.source_subfolder + "/CMakeLists.txt", "PKG_CHECK_MODULES(LIBSSH2 libssh2)", "FIND_PACKAGE(LIBSSH2)")
            copy2(self.source_folder + "/FindLIBSSH2.cmake", self.source_subfolder + "/cmake/Modules", )

        cmake = CMake(self)
        cmake.definitions["BUILD_CLAR"] = False
        cmake.definitions["THREADSAFE"] = self.options.threadsafe
        cmake.definitions["USE_SHA1DC"] = self.options.use_sha1dc
        cmake.definitions["USE_ICONV"] = self.options.use_iconv
        cmake.definitions["USE_SSH"] = self.options.with_ssh

        # if self.options.with_ssh:
        #     cmake.definitions["CMAKE_INCLUDE_PATH"] =  self.deps_cpp_info['libssh2'].include_paths[0]
        #     cmake.definitions["CMAKE_LIBRARY_PATH"] =  self.deps_cpp_info['libssh2'].lib_paths[0]

  #         Add the installation prefix of "LIBCURL" to CMAKE_PREFIX_PATH or set
  # "LIBCURL_DIR" to a directory containing one of the above files.  If
  # "LIBCURL" provides a separate development package or SDK, be sure it has
  # been installed.

        cmake.definitions["USE_OPENSSL"] = self.options.with_openssl

        if self.settings.os == "Windows":
            cmake.definitions["WINHTTP"] = self.options.use_winhttp
            if self.settings.compiler == "Visual Studio":
                cmake.definitions["STATIC_CRT"] = self.settings.compiler.runtime == "MT"

        cmake.configure(build_folder=self.build_subfolder)
        cmake.build()

    def package(self):
        include_folder = os.path.join(self.source_subfolder, "include")
        self.copy(pattern="LICENSE", dst="license", src=self.source_subfolder)
        self.copy(pattern="*", dst="include", src=include_folder)
        self.copy(pattern="*.dll", dst="bin", keep_path=False)
        self.copy(pattern="*.lib", dst="lib", keep_path=False)
        self.copy(pattern="*.a", dst="lib", keep_path=False)
        self.copy(pattern="*.so*", dst="lib", keep_path=False)
        self.copy(pattern="*.dylib", dst="lib", keep_path=False)


    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)

        if self.settings.os == "Windows":
            self.cpp_info.libs.append("winhttp.lib")
            self.cpp_info.libs.append("Rpcrt4.lib")
            self.cpp_info.libs.append("Crypt32.lib")
        if tools.os_info.is_macos:
            self.cpp_info.libs.append("curl")
            self.cpp_info.exelinkflags.append("-framework Cocoa")
            self.cpp_info.exelinkflags.append("-framework Security")
            self.cpp_info.sharedlinkflags = self.cpp_info.exelinkflags

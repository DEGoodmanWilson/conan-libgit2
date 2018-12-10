#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re


from bincrafters import build_template_default

def get_value_from_recipe(search_string):
    with open("conanfile.py", "r") as conanfile:
        contents = conanfile.read()
        result = re.search(search_string, contents)
    return result


def get_name_from_recipe():
    return get_value_from_recipe(r'''name\s*=\s*["'](\S*)["']''').groups()[0]

if __name__ == "__main__":
    name = get_name_from_recipe()
    username, channel, version, login_username = get_conan_vars()
    reference = "{0}/{1}".format(name, version)
    upload = get_conan_upload(username)
    bincrafters = "https://api.bintray.com/conan/bincrafters/public-conan"

    builder = build_template_default.get_builder(remotes=[upload, bincrafters])

    builder.run()
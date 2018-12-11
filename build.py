#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import os

from bincrafters import build_template_default, build_shared
from cpt.packager import ConanMultiPackager

if __name__ == "__main__":
    name = build_shared.get_name_from_recipe()
    username, channel, version, login_username = build_shared.get_conan_vars()
    reference = "{0}/{1}".format(name, version)
    upload = "https://api.bintray.com/conan/{0}/opensource".format(username.lower())
    bincrafters = "https://api.bintray.com/conan/bincrafters/public-conan"
    remotes = os.getenv("CONAN_REMOTES", [upload, bincrafters])
    upload_when_stable = build_shared.get_upload_when_stable()
    stable_branch_pattern = os.getenv("CONAN_STABLE_BRANCH_PATTERN", "stable/*")
    archs = build_shared.get_archs()
    builder = ConanMultiPackager(
        username=username,
        login_username=login_username,
        channel=channel,
        reference=reference,
        upload=upload,
        remotes=remotes,
        archs=archs,
        upload_only_when_stable=upload_when_stable,
        stable_branch_pattern=stable_branch_pattern)

    builder.add_common_builds(shared_option_name=name + ":shared")
    builder.run()
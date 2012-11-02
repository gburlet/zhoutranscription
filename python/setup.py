import os
import sys
from setuptools import setup, Extension

if sys.platform == "darwin":
    link_args = []
    libraries = ["boost_python-mt", "ztranscribe", "boost_numpy"]
    library_dirs = ["/usr/local/lib"]
    include_dirs = [".."]
    runtime_library_dirs = ["/usr/local/lib"]

setup(
    name = "ztranscription",
    version = "0.0.1",
    author = "Gregory Burlet",
    author_email = "gregory.burlet@mail.mcgill.ca",
    description = ("Polyphonic transcription using Zhou et al. (2009)"),
    license = "BSD",
    keywords = "polyphonic transcription",
    url = "https://github.com/gburlet/zhoutranscription",
    packages = ["ztranscribe"],
    long_description="Input audio, output note events.",
    classifiers=["Development Status :: 3 - Alpha"],
    ext_modules = [
        Extension("ztranscribe.transcribe",
            ["src/_ztranscribe.cpp"],
            libraries=libraries,
            extra_link_args=link_args,
            library_dirs=library_dirs,
            runtime_library_dirs=runtime_library_dirs,
            include_dirs=include_dirs,
            extra_compile_args=['-g']
        )
    ]
)

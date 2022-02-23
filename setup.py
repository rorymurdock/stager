import setuptools
from stager.utils.constants import APPLICATION_VERSION

with open("README.md", "r") as fh:
    LONG_DESCRIPTION = fh.read()

setuptools.setup(
    name="stager",
    version=APPLICATION_VERSION,
    author="Rory Murdock",
    author_email="rorym@rorymurdock.com.au",
    description="Staging tool GUI",
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    url="",
    packages=setuptools.find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: Unix",
    ],
    install_requires=[],
    include_package_data=True,
    entry_points={
        "gui_scripts": [
            "stager = stager.__main__:main"
        ]
    },
)

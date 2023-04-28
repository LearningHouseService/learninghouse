from os import path

import setuptools

import versioneer

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = fh.readlines()


packages = setuptools.find_packages(exclude=["tests"])
packages.append("learninghouse.static")
packages.append("learninghouse.static.docs")
if path.exists("learninghouse/ui"):
    packages.append("learninghouse.ui")
    packages.append("learninghouse.ui.assets")
    packages.append("learninghouse.ui.assets.fonts")
    packages.append("learninghouse.ui.assets.i18n")

setuptools.setup(
    name="learninghouse",
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    description="learningHouse - Teach your smart home everything",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/LearningHouseService/learninghouse-monorepo",
    author="Johannes Ott",
    author_email="info@johannes-ott.net",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Topic :: Home Automation",
        "License :: OSI Approved :: MIT License",
        "Framework :: FastAPI",
        "Natural Language :: English",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.10",
    ],
    keywords="smart home, machine learning, house automation",
    packages=packages,
    include_package_data=True,
    python_requires=">=3.10, <4",
    install_requires=[req for req in requirements if req[:2] != "# "],
    entry_points={"console_scripts": ["learninghouse=learninghouse.service:run"]},
    project_urls={
        "Bug Reports": "https://github.com/LearningHouseService/learninghouse/issues"
    },
)

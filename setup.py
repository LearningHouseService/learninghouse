import setuptools
import versioneer

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = fh.readlines()

packages = setuptools.find_packages(exclude=['tests'])
packages.append('learninghouse.static')
packages.append('learninghouse.static.docs')

setuptools.setup(
    name='learninghouse',
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    description='learningHouse - Teach your smart home everything',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/LearningHouseService/learninghouse-core',
    author='Johannes Ott',
    author_email='info@johannes-ott.net',
    classifiers=[
        'Development Status :: 5 - Production/Stable',

        'Topic :: Home Automation',

        'License :: OSI Approved :: MIT License',

        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3 :: Only',
    ],
    keywords='smart home, machine learning, house automation',
    packages=packages,
    include_package_data=True,
    python_requires='>=3.6, <4',
    install_requires=[req for req in requirements if req[:2] != "# "],
    entry_points={
        'console_scripts': [
            'learninghouse=learninghouse.service:run'
        ]
    },
    project_urls={
        'Bug Reports': 'https://github.com/LearningHouseService/learninghouse-core/issues'
    }
)

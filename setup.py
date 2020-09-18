from setuptools import setup
from learninghouse.service import version
import pathlib

here = pathlib.Path(__file__).parent.resolve()

# Get the long description from the README file
long_description = (here / 'README.md').read_text(encoding='utf-8')

setup(
    name='learninghouse',
    version=version,
    description='learningHouse - Teach your smart home everything',
    long_description=long_description,
    long_description_content_type='text/markdown',        
    url='https://github.com/LearningHouseService/learninghouse-core',
    author='Johannes Ott',
    author_email='info@johannes-ott.net',
    classifiers=[ 
        'Development Status :: 3 - Alpha',

        'Topic :: Home Automation',

        'License :: OSI Approved :: MIT License',

        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3 :: Only',
    ],
    keywords='smart home, machine learning, house automation',
    package_dir={'learninghouse': 'learninghouse'},
    packages=['learninghouse'],
    python_requires='>=3.6, <4',
    install_requires = [
        'waitress', 
        'flask', 'flask_restful',
        'click', 
        'pyyaml',
        'numpy', 'pandas',
        'scikit-learn'
    ],
    entry_points={
        'console_scripts': [
            'learninghouse=learninghouse.cli:cli'
        ]
    },
    project_urls={
        'Bug Reports': 'https://github.com/LearningHouseService/learninghouse-core/issues'
    }
)
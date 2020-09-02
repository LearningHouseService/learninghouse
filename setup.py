from setuptools import setup

setup(name='learninghouse',
      version='0.3',
      description='learningHouse - Teach your smart home everything',
      url='https://github.com/LearningHouseService/learninghouse-core',
      author='Johannes Ott',
      author_email='info@johannes-ott.net',
      license='MIT',
      install_requires = [
          'uwsgi', 'flask', 'flask_restful', 
          'numpy', 'pandas',
          'scikit-learn'
      ]
)
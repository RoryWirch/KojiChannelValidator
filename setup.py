from setuptools import setup
setup(
  name = 'koji-channel-validator',
  packages = ['koji-channel-validator'],
  version = '0.1',
  license='MIT',
  description = 'Identify system resource drift across many Koji builders',
  author = 'Rory Wirch',
  url = 'https://github.com/RoryWirch/koji-channel-validator',
  install_requires=[
          #TODO: 'here',
      ],
  classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
from setuptools import setup
setup(
  name = 'KojiChannelValidator',
  packages = ['kojichannelvalidator'],
  version = '0.1',
  license='MIT',
  description = 'Identify system resource drift across many Koji builders',
  author = 'Rory Wirch',
  url = 'https://github.com/RoryWirch/KojiChannelValidator',
  install_requires=[
        "requests",
        "koji"
      ],
  classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
  entry_points={
    "console_scripts":[
      "kcv=kojichannelvalidator.__main__:main",
    ]
  },
)
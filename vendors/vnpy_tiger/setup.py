from setuptools import setup, find_packages

setup(
    name="vnpy_tiger",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    license="MIT",
    url="https://github.com/vnpy/vnpy_tiger",
    description="Tiger Securities gateway for VeighNa",
    packages=find_packages(include=["vnpy_tiger", "vnpy_tiger.*"]),
    install_requires=[
        "vnpy",
        "tigeropen",
    ],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: Unix",
        "Operating System :: POSIX",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Office/Business :: Financial :: Investment",
        "Programming Language :: Python :: Implementation :: CPython",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: Chinese (Simplified)",
        "Natural Language :: Chinese (Traditional)",
        "Natural Language :: English"
    ]
)

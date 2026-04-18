from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="crontab-buddy",
    version="0.1.0",
    description="Interactively build, validate, and document cron expressions with human-readable previews",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="crontab-buddy contributors",
    python_requires=">=3.8",
    packages=find_packages(),
    install_requires=[],
    extras_require={
        "dev": [
            "pytest>=7.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "crontab-buddy=crontab_buddy.cli:main",
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Environment :: Console",
        "Topic :: Utilities",
    ],
)

from setuptools import setup, find_packages

setup(
    name="sudoku-game",
    version="1.0.0",
    description="لعبة سودوكو احترافية بلغة بايثون مع واجهة رسومية تفاعلية",
    author="Sudoku Game Developer",
    packages=find_packages(),
    install_requires=[
        "pygame>=2.5.2",
    ],
    python_requires=">=3.6",
    entry_points={
        "console_scripts": [
            "sudoku=sudoku_game:main",
        ],
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)
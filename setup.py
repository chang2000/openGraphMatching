import setuptools
with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="openGraphMatching",
    version="0.2.1",
    author="WANG Tianchang, LI Yuxiang",
    author_email="tianchang.wang.00@gmail.com",
    description="A subgraph matching programming library.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/chang2000/openGraphMatching",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)

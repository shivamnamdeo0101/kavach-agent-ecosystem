from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="kavach-mcp-events",
    version="0.0.2",
    description="Event bus for Kavach security middleware lifecycle hooks",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Shivam Namdeo",
    author_email="shivamnamdeo0101@gmail.com",
    url="https://github.com/shivamnamdeo0101/kavach-agent-ecosystem",
    license="MIT",
    packages=find_packages(),
    python_requires=">=3.7",
    install_requires=[],
)

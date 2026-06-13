from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="kavach-shield",
    version="0.0.3",
    description="Security middleware for Model Context Protocol (MCP) - detection engine and rules",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Shivam Namdeo",
    author_email="shivamnamdeo0101@gmail.com",
    url="https://github.com/shivamnamdeo0101/kavach-agent-ecosystem",
    license="MIT",
    packages=find_packages(),
    python_requires=">=3.7",
    install_requires=[
        "kavach-logger>=0.0.3",
        "kavach-mcp-events>=0.0.3",
        "fastmcp>=0.1.0",
    ],
)

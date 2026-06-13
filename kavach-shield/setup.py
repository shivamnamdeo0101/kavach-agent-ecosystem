from setuptools import setup, find_packages

setup(
    name="kavach-shield",
    version="0.1.0",
    description="Security middleware for Model Context Protocol (MCP) - detection engine and rules",
    author="Shivam Namdeo",
    author_email="shivamnamdeo0101@gmail.com",
    url="https://github.com/shivamnamdeo0101/kavach-agent-ecosystem",
    license="MIT",
    packages=find_packages(),
    python_requires=">=3.7",
    install_requires=[
        "kavach-logger>=0.1.0",
        "kavach-mcp-events>=0.1.0",
    ],
)

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="kavach-mcp-gateway",
    version="0.0.1",
    description="Config-driven API gateway for Model Context Protocol (MCP) - dynamic routing via YAML",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Shivam Namdeo",
    author_email="shivamnamdeo0101@gmail.com",
    url="https://github.com/shivamnamdeo0101/kavach-agent-ecosystem",
    license="MIT",
    packages=find_packages(),
    python_requires=">=3.7",
    install_requires=[
        "PyYAML>=5.3",
        "httpx>=0.23.0",
        "kavach-logger>=0.0.3",
        "kavach-mcp-events>=0.0.3",
    ],
    extras_require={
        "security": ["kavach-shield>=0.0.3"],
    },
)

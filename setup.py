#!/usr/bin/env python3
"""Setup script for MCP Document Converter"""

from setuptools import setup, find_packages
import os
import json

# 读取mcp.json配置
with open('mcp.json', 'r', encoding='utf-8') as f:
    mcp_config = json.load(f)

# 读取README文件
with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

# 读取requirements.txt
with open('requirements.txt', 'r', encoding='utf-8') as f:
    requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]

setup(
    name=mcp_config['name'],
    version=mcp_config['version'],
    description=mcp_config['description'],
    long_description=long_description,
    long_description_content_type='text/markdown',
    author=mcp_config['author'],
    license=mcp_config['license'],
    url=mcp_config.get('homepage', ''),
    project_urls={
        'Repository': mcp_config.get('repository', {}).get('url', ''),
        'Bug Reports': mcp_config.get('repository', {}).get('url', '') + '/issues',
    },
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    python_requires=mcp_config['python_requires'],
    install_requires=requirements,
    keywords=mcp_config['keywords'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Topic :: Office/Business :: Office Suites',
        'Topic :: Text Processing :: Markup',
        'Topic :: Utilities',
    ],
    entry_points={
        'console_scripts': [
            'mcp-document-converter=mcp_document_converter.server:main',
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
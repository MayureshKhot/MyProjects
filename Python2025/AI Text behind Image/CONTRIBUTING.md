# Contributing to AI Text Behind Image

Thank you for your interest in contributing to the AI Text Behind Image project! This document provides guidelines and instructions for contributing to the project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [How to Contribute](#how-to-contribute)
  - [Reporting Bugs](#reporting-bugs)
  - [Suggesting Enhancements](#suggesting-enhancements)
  - [Code Contributions](#code-contributions)
- [Development Setup](#development-setup)
- [Pull Request Process](#pull-request-process)
- [Style Guidelines](#style-guidelines)
- [Testing](#testing)
- [Documentation](#documentation)

## Code of Conduct

This project and everyone participating in it is governed by our Code of Conduct. By participating, you are expected to uphold this code. Please report unacceptable behavior to the project maintainers.

## Getting Started

1. Fork the repository on GitHub
2. Clone your fork locally
3. Set up the development environment (see [Development Setup](#development-setup))
4. Create a new branch for your contribution

## How to Contribute

### Reporting Bugs

Before creating bug reports, please check the issue tracker to see if the problem has already been reported. If it hasn't, create a new issue with the following information:

- A clear and descriptive title
- Steps to reproduce the issue
- Expected behavior
- Actual behavior
- Screenshots (if applicable)
- System information (OS, Python version, etc.)

You can generate a system report using the provided utility:

```
python generate_report.py --output bug_report.txt
```

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion, include:

- A clear and descriptive title
- Detailed explanation of the proposed feature
- Examples of how the feature would be used
- Any relevant mockups or diagrams

### Code Contributions

1. Ensure your code follows the project's style guidelines
2. Add or update tests as necessary
3. Update documentation to reflect your changes
4. Submit a pull request with a clear description of the changes

## Development Setup

1. Clone your fork of the repository
   ```
   git clone https://github.com/YOUR_USERNAME/ai-text-behind-image.git
   cd ai-text-behind-image
   ```

2. Create a virtual environment
   ```
   # Windows
   python -m venv venv
   venv\Scripts\activate

   # Linux/macOS
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Install dependencies
   ```
   pip install -r requirements.txt
   pip install -r dev-requirements.txt  # Development dependencies
   ```

4. Run the system check to verify your setup
   ```
   python check_system.py
   ```

## Pull Request Process

1. Update the README.md with details of changes to the interface, if applicable
2. Update the documentation with any new information
3. The PR should work for all supported platforms (Windows, macOS, Linux)
4. Ensure all tests pass
5. Get approval from at least one project maintainer

## Style Guidelines

### Code Style

- Follow PEP 8 style guidelines for Python code
- Use meaningful variable and function names
- Include docstrings for all functions, classes, and modules
- Keep functions focused on a single responsibility
- Comment complex code sections

### Commit Messages

- Use the present tense ("Add feature" not "Added feature")
- Use the imperative mood ("Move cursor to..." not "Moves cursor to...")
- Limit the first line to 72 characters or less
- Reference issues and pull requests after the first line

## Testing

- Write tests for all new features and bug fixes
- Ensure all tests pass before submitting a pull request
- Run the test suite using the provided utility:
  ```
  python run_tests.py --all
  ```

## Documentation

- Update the README.md file with any necessary changes
- Document all new features, options, and commands
- Keep API documentation up-to-date
- Include examples for new functionality

---

Thank you for contributing to AI Text Behind Image!
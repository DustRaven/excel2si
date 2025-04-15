# Contributing to CSV2JSON Converter

Thank you for your interest in contributing to CSV2JSON Converter! This document provides guidelines and instructions for contributing.

## Code of Conduct

Please be respectful and considerate of others when contributing to this project.

## How to Contribute

### Reporting Bugs

1. Check if the bug has already been reported in the [Issues](https://github.com/DustRaven/csv2json/issues)
2. If not, create a new issue using the bug report template
3. Include as much detail as possible:
   - Steps to reproduce
   - Expected behavior
   - Actual behavior
   - Screenshots if applicable
   - Sample files that demonstrate the issue (with sensitive data removed)

### Suggesting Features

1. Check if the feature has already been suggested in the [Issues](https://github.com/DustRaven/csv2json/issues)
2. If not, create a new issue using the feature request template
3. Clearly describe the feature and its benefits

### Pull Requests

1. Fork the repository
2. Create a new branch for your changes
3. Make your changes
4. Write or update tests as needed
5. Ensure all tests pass
6. Submit a pull request

#### Pull Request Guidelines

- Use a clear and descriptive title
- Follow the pull request template
- Reference any related issues
- Update documentation as needed
- Make sure your code follows the project's style guidelines

## Development Setup

1. Clone the repository:
   ```
   git clone https://github.com/DustRaven/csv2json.git
   cd csv2json
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Install the package in development mode:
   ```
   pip install -e .
   ```

## Testing

Run tests with:
```
pytest
```

## Style Guidelines

- Follow PEP 8 for Python code
- Use meaningful variable and function names
- Write docstrings for all functions, classes, and modules
- Keep functions small and focused on a single task

## Commit Messages

- Use clear and meaningful commit messages
- Start with a verb in the present tense (e.g., "Add", "Fix", "Update")
- Reference issue numbers when applicable

## Release Process

This project uses GitHub's Release Drafter to automate the creation of release notes:

1. Pull requests are automatically labeled based on their title and description
2. When PRs are merged to the main branch, a draft release is created or updated
3. Release notes are categorized based on PR labels (features, bug fixes, etc.)
4. When ready to release, a maintainer publishes the draft release with a new version tag
5. The tag triggers the build workflow which creates the executable

To contribute effectively:
- Make sure your PR title clearly describes the change
- Use conventional prefixes like "Fix:", "Feature:", or "Docs:" in PR titles when possible
- Review the automatically applied labels and adjust if needed

## Thank You!

Your contributions help make CSV2JSON Converter better for everyone!

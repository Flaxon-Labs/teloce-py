# Contributing to Teloce-Py

Thank you for considering contributing to Teloce-Py!

## Code of Conduct

Please read and follow our [Code of Conduct](CODE_OF_CONDUCT.md).

## How to Contribute

### Reporting Bugs

1. Check if the bug has already been reported
2. Create a new issue with:
   - A clear title
   - Steps to reproduce
   - Expected behavior
   - Actual behavior
   - Environment details

### Suggesting Features

1. Check if the feature already exists or is planned
2. Create a new issue with:
   - A clear title
   - Detailed description
   - Use case
   - Possible implementation approach

### Pull Requests

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Make your changes
4. Write tests for your changes
5. Run the test suite: `pytest`
6. Commit your changes: `git commit -m "feat: add your feature"`
7. Push to your fork: `git push origin feature/your-feature`
8. Open a Pull Request

## Development Setup

### Prerequisites

- Python 3.9 or higher
- Git

### Setup

```bash
# Clone the repository
git clone https://github.com/telocejs/teloce-py.git
cd teloce-py

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest


Project Structure
text
teloce-py/
├── src/teloce/     # Main package
├── tests/          # Test suite
├── examples/       # Example projects
└── docs/           # Documentation
Code Style
Follow PEP 8

Use Black for formatting

Use isort for import sorting

Use mypy for type checking

bash
# Format code
black src/ tests/

# Sort imports
isort src/ tests/

# Type check
mypy src/
Commit Convention
We use Conventional Commits:

feat: New feature

fix: Bug fix

docs: Documentation

style: Code style

refactor: Code refactor

perf: Performance improvement

test: Tests

chore: Maintenance

Testing
Write tests for all new features and bug fixes.

bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_compiler.py

# Run with coverage
pytest --cov=teloce
Documentation
Update documentation for all new features.

User guide: docs/

API documentation: In code (docstrings)

README: Project overview

License
By contributing, you agree that your contributions will be licensed under the MIT License.
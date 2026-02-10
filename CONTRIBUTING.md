# Contributing to Auxobots

Thank you for considering contributing to Auxobots!  
We welcome bug reports, feature suggestions, documentation improvements, code fixes, new tests, and even new exchange/strategy adapters (as long as they follow the project's architecture).

## Ways to Contribute

- Reporting bugs or unexpected behavior
- Suggesting new features or improvements
- Improving documentation (README, code comments, wiki pages)
- Fixing typos or formatting issues
- Writing or improving tests
- Submitting code fixes or new functionality
- Helping review pull requests
- Answering questions in issues/discussions

## How to Contribute

### 1. Before you start

- Check the [existing issues](https://github.com/aulekator/auxobots/issues) — your bug or idea might already be reported.
- If you're planning a large change (new strategy, major refactor, new exchange), please open an issue first to discuss it.

### 2. Development setup

Follow the steps in the [README.md](./README.md) → Installation section.

Quick reminder:

git clone https://github.com/aulekator/auxobots.git
cd auxobot
python -m venv venv
source venv/bin/activate    # or equivalent for Windows
pip install -r requirements.txt
python manage.py migrate
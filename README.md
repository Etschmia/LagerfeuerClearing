# Lagerfeuer Clearing

A tool for groups of friends to split expenses during trips or events. Track who paid for what, manage groups, and calculate optimal repayment plans to minimize the number of transactions.

## Installation

### From Source

```bash
# Clone the repository
git clone https://github.com/example/lagerfeuer-clearing.git
cd lagerfeuer-clearing

# Install the package using uv (recommended)
uv pip install -e .

# Or using pip
pip install -e .
```

## Development

This project uses `uv` for fast dependency management and running Python code. If you don't have it installed, you can install it with:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Setting up a development environment

```bash
# Create and activate a virtual environment
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install the package in development mode
uv pip install -e .

# Install development dependencies
uv pip install ruff pytest
```

## Project Structure

The project is organized as a proper Python package:

```
lagerfeuer_clearing/
├── __init__.py         # Package metadata
├── __main__.py         # Entry point
├── core/               # Core functionality
│   ├── __init__.py
│   └── expense_manager.py
├── cli/                # Command-line interface
│   ├── __init__.py
│   └── cli_app.py
├── gui/                # Graphical user interface
│   ├── __init__.py
│   └── gui_app.py
├── tests/              # Test suite
│   ├── __init__.py
│   ├── test_expense_manager.py
│   └── run_tests.py
└── examples/           # Example scripts
    ├── __init__.py
    └── weekend_trip.py
```

## Project Configuration

The project uses modern Python packaging tools:

- **pyproject.toml**: Configuration for build system, project metadata, and development tools like Ruff
  
The configuration defines the following entry points:

- `lagerfeuer-cli`: Command-line interface
- `lagerfeuer-gui`: Graphical interface
- `lagerfeuer`: Default entry point (GUI with `--cli` option)

## Features

- Track expenses paid by different people
- Define groups of people to share specific costs
- Record prepayments between individuals
- Calculate optimal repayment plans to minimize transactions
- Save and load data from JSON files
- Export results as text files
- Visualize individual balances and transaction history

## Usage

### Command Line Interface

```bash
# Run as an installed package
lagerfeuer-cli

# Run directly from the module
python -m lagerfeuer_clearing --cli

# Run the script directly
python lagerfeuer_clearing/cli/cli_app.py
```

### Graphical User Interface

```bash
# Run as an installed package
lagerfeuer-gui

# Run directly (default interface)
lagerfeuer
python -m lagerfeuer_clearing

# Run the script directly
python lagerfeuer_clearing/gui/gui_app.py
```

The GUI application has four tabs:
1. **Gruppen (Groups)**: Manage groups of people
2. **Ausgaben (Expenses)**: Add, edit, and remove expenses
3. **Anzahlungen (Prepayments)**: Track payments made between individuals
4. **Ergebnisse (Results)**: View calculations and save results

The application automatically saves data to `expense_data.json` when you click the "Speichern" button.

## Using the ExpenseManager Class

You can also use the `ExpenseManager` class directly in your own applications:

```python
from lagerfeuer_clearing.core import ExpenseManager

# Create with default example data
manager = ExpenseManager.create_with_defaults()

# Or create with your own data
manager = ExpenseManager(
    persons=["Alice", "Bob", "Charlie"],
    groups={"All": ["Alice", "Bob", "Charlie"]},
    expenses=[{"person": "Alice", "amount": 150, "group": "All", "subject": "Food"}],
    prepayments=[]
)

# Calculate and print results
results = manager.calculate_transactions()
print(manager.get_summary())

# Save data
manager.save_to_file("my_trip.json")
```

See `lagerfeuer_clearing/examples/weekend_trip.py` for a complete example.

## Testing

Run the tests using:

```bash
# Run tests using uv (recommended)
uv run -m lagerfeuer_clearing.tests.run_tests

# Alternatively with Python
python -m lagerfeuer_clearing.tests.run_tests

# Or use unittest directly
python -m unittest discover -s lagerfeuer_clearing/tests
```

## Linting

This project uses `ruff` for linting:

```bash
# Install ruff if not installed
uv pip install ruff

# Run linting checks
ruff check .

# Auto-fix issues
ruff check --fix .
```

## Continuous Integration

This project uses GitHub Actions to run tests and linting checks automatically on each push:

- **What it does**: Runs tests and linting checks (ruff) on Python 3.11
- **When it runs**: On each push to main branch and on pull requests to main
- **How to check**: Visit the Actions tab on the GitHub repository page
- **Configuration**: See `.github/workflows/test-and-lint.yml`

## Contributing

Contributions are welcome! Here's how to contribute to the project:

1. **Fork the repository** and clone it locally
2. **Create a virtual environment** using `uv venv` and activate it
3. **Install dependencies**:
   ```bash
   uv pip install -e .
   uv pip install ruff pytest
   ```
4. **Create a branch** for your feature or bugfix:
   ```bash
   git checkout -b feature/your-feature-name
   ```
5. **Make your changes**
6. **Run tests and linting locally** before committing:
   ```bash
   # Run tests
   uv run -m lagerfeuer_clearing.tests.run_tests
   
   # Run linting
   ruff check .
   
   # Fix linting issues automatically
   ruff check --fix .
   ```
7. **Commit your changes** with a clear commit message
8. **Push to your fork** and submit a pull request

The GitHub Actions workflow will automatically run tests and linting on your pull request.

## Requirements

- Python 3.11+
- tkinter (for GUI version, included in standard Python distribution) 
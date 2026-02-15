# Contributing to Steam Workshop Collection Toolkit

Thank you for your interest in contributing! This document provides guidelines and instructions.

## Code Structure

The project is organized into three main modules:

### 1. **core/** - Business Logic
Contains all the core functionality:
- `api.py` - Steam API interactions
- `categories.py` - Category management
- `csv_manager.py` - CSV file operations
- `steam_collection.py` - Steam collection operations
- `collectionfromcsv.py` - Bulk add operations

**When to modify:**
- Adding new API features
- Changing how data is processed
- Adding new business logic

### 2. **ui/** - User Interfaces
Provides access to features:
- `console.py` - Terminal interface
- `gui.py` - Tkinter GUI interface

**When to modify:**
- Improving UI/UX
- Adding new interface options
- Changing how features are presented

### 3. **utils/** - Utilities
Helper functions and management:
- `settings_manager.py` - Configuration and progress tracking
- `file_utils.py` - JSON I/O operations
- `input_handlers.py` - User input dialogs

**When to modify:**
- Improving configuration handling
- Adding new utility functions
- Changing how settings are stored

## Getting Started

1. **Fork and clone**
```bash
git clone https://github.com/yourusername/steam-workshop-toolkit.git
cd steam-workshop-toolkit
```

2. **Create virtual environment**
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
```

3. **Install development dependencies**
```bash
pip install -r workshop/requirements.txt
```

## Making Changes

### Naming Conventions
- Functions: `snake_case`
- Classes: `PascalCase`
- Constants: `UPPER_SNAKE_CASE`
- Private functions: `_snake_case`

### Code Style
- Use type hints where possible
- Add docstrings to functions
- Keep lines under 100 characters
- Use 4 spaces for indentation

### Example Function
```python
def process_mods(mod_ids: list[int], game_name: str) -> dict[str, list]:
    """
    Process and organize mods by category.
    
    Args:
        mod_ids: List of mod IDs to process
        game_name: Name of the game
        
    Returns:
        Dictionary mapping category names to mod lists
    """
    # Implementation...
```

## Testing Changes

Before submitting:

1. **Test the console interface**
```bash
python workshop/main.py
# Test relevant feature
```

2. **Test the GUI**
Edit `params.json`:
```json
{"use_gui": true}
```
```bash
python workshop/main.py
# Test relevant feature
```

3. **Check imports**
Ensure new modules are exported in respective `__init__.py` files

## Submitting Changes

### Pull Request Process

1. **Create feature branch**
```bash
git checkout -b feature/your-feature-name
```

2. **Make your changes**
- Follow code style guidelines
- Add/update docstrings
- Update `__all__` exports if needed

3. **Test thoroughly**
- Test on both console and GUI if applicable
- Test error cases
- Verify no new imports break anything

4. **Commit clearly**
```bash
git commit -m "Add feature: clear description"
```

5. **Push and create PR**
```bash
git push origin feature/your-feature-name
```

In your PR description:
- Describe what you changed
- Explain why this change is needed
- List any breaking changes
- Include testing steps

## Common Contribution Types

### Adding a New Feature

1. Implement in appropriate module (core/ui/utils)
2. Add to `__init__.py` exports
3. Update README.md with usage
4. Test in both console and GUI if applicable

### Fixing a Bug

1. Create issue describing the bug
2. Create PR with fixes
3. Reference the issue in PR description
4. Add regression test if applicable

### Improving Documentation

1. Update README.md or docstrings
2. Add examples if helpful
3. Keep consistent with existing style

### Optimizing Performance

1. Benchmark before and after
2. Document improvements in commit message
3. Ensure no functionality changes

## Issues and Discussions

### Reporting Bugs

Create an issue with:
- Python version
- OS and environment
- Steps to reproduce
- Expected vs actual behavior
- Error messages/logs

### Proposing Features

Create an issue with:
- Clear description of feature
- Use cases and benefits
- Potential implementation approach
- Any concerns or limitations

## Code Review Process

Contributors should expect:
1. Initial review within 1 week
2. Feedback on code style, logic, or design
3. Requests for additional tests
4. Discussion of larger architectural changes

## Questions?

- Check existing issues/discussions
- Review code examples in README
- Examine existing implementations

## Thank You!

Your contributions make this project better for everyone. We appreciate your effort and time!

---

**Happy contributing! 🚀**

# Contributing to DJI Video to 3D Map Pipeline

Thank you for your interest in contributing! This document provides guidelines for contributing to the project.

## How to Contribute

### Reporting Bugs

1. **Check existing issues** to avoid duplicates
2. **Create a new issue** with:
   - Clear, descriptive title
   - Steps to reproduce
   - Expected vs actual behavior
   - System information (Windows version, Python version)
   - Sample data if applicable (without sensitive info)

### Suggesting Enhancements

1. **Open an issue** describing:
   - The problem you're trying to solve
   - Your proposed solution
   - Why this enhancement would be useful
   - Alternative solutions you've considered

### Pull Requests

1. **Fork the repository**
2. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. **Make your changes**:
   - Follow the existing code style
   - Add tests for new functionality
   - Update documentation as needed
4. **Test your changes**:
   ```bash
   pytest test_*.py -v
   ```
5. **Commit your changes**:
   ```bash
   git commit -m "Add feature: description"
   ```
6. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```
7. **Open a Pull Request**

## Development Setup

```bash
# Clone your fork
git clone https://github.com/YOUR-USERNAME/Video-SRT_to_3D_Map.git
cd Video-SRT_to_3D_Map

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install dev dependencies
pip install pytest pytest-cov black flake8
```

## Code Style

### Python
- Follow **PEP 8** style guide
- Use **meaningful variable names**
- Add **docstrings** to functions and classes
- Keep functions **focused and small**
- Use **type hints** where appropriate

### Example:
```python
def parse_telemetry(srt_file: str) -> pd.DataFrame:
    """
    Parse DJI SRT telemetry file.
    
    Args:
        srt_file: Path to SRT file
        
    Returns:
        DataFrame with telemetry data
    """
    # Implementation
    pass
```

## Testing

### Writing Tests
- Place tests in `test_*.py` files
- Use descriptive test names
- Test edge cases and error conditions
- Aim for >80% code coverage

### Running Tests
```bash
# Run all tests
pytest test_*.py -v

# Run with coverage
pytest test_*.py --cov=. --cov-report=html

# Run specific test
pytest test_srt_parser.py::TestSRTParser::test_parse_srt_file -v
```

## Documentation

### Code Documentation
- Add docstrings to all public functions
- Include type hints
- Explain complex algorithms
- Add inline comments for clarity

### User Documentation
- Update README.md for new features
- Add examples to QUICKSTART.md
- Update version numbers appropriately

## Project Structure

```
Video-SRT_to_3D_Map/
├── main_app.py           # GUI application
├── srt_parser.py         # SRT parsing
├── frame_extractor.py    # Video processing
├── telemetry_sync.py     # Synchronization
├── exif_injector.py      # Metadata injection
├── webodm_client.py      # WebODM API
├── test_*.py             # Unit tests
├── config.py             # Configuration
├── build.py              # Build script
├── requirements.txt      # Dependencies
├── README.md             # Main documentation
├── QUICKSTART.md         # Quick start guide
├── LICENSE               # License file
├── CONTRIBUTING.md       # This file
└── .github/
    └── workflows/
        └── build.yml     # CI/CD workflow
```

## Feature Areas

### High Priority
- [ ] Google Drive integration
- [ ] Batch processing
- [ ] Additional drone models support
- [ ] Progress persistence
- [ ] Error recovery

### Medium Priority
- [ ] Custom processing presets
- [ ] GPS path visualization
- [ ] Quality metrics
- [ ] Video preview
- [ ] Export format options

### Low Priority
- [ ] Plugin system
- [ ] Custom themes
- [ ] Multi-language support
- [ ] Cloud processing

## Commit Message Guidelines

Use clear, descriptive commit messages:

```
Add feature: SRT parsing for DJI Mini 3
Fix: Handle missing GPS coordinates
Refactor: Improve interpolation performance
Docs: Update installation instructions
Test: Add tests for circular interpolation
```

## Review Process

1. **Automated checks** must pass:
   - Tests
   - Code style
   - Build success

2. **Manual review** by maintainers:
   - Code quality
   - Documentation
   - Test coverage
   - Feature completeness

3. **Approval and merge**

## Questions?

- Open an issue for questions
- Tag with `question` label
- We're happy to help!

## Code of Conduct

Be respectful, inclusive, and professional:
- ✅ Constructive feedback
- ✅ Collaborative approach
- ✅ Welcoming environment
- ❌ Harassment or discrimination
- ❌ Personal attacks
- ❌ Disruptive behavior

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing! 🙏

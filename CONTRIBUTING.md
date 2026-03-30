# Contributing to LLM Wrapper

Thank you for considering contributing to this project! We welcome all kinds of contributions.

## Before You Start

1. **Read the [SECURITY.md](SECURITY.md) file** - Learn about sensitive files and credentials
2. **Never commit `.env` files or API keys** - Use `.env.example` as a template
3. **Fork the repository** and create a feature branch

## How to Contribute

### Setting Up Development Environment

1. Fork and clone the repository:
   ```bash
   git clone https://github.com/YOUR-USERNAME/slmoi.git
   cd slmoi
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your API keys (see README.md for where to get them)
   ```

4. Run locally:
   ```bash
   python main.py
   ```

### Reporting Issues

Found a bug or have a feature request?

1. **Check existing issues** to avoid duplicates
2. **Open a new issue** with:
   - Clear title and description
   - Steps to reproduce (for bugs)
   - Expected vs actual behavior
   - Your environment (OS, Python version)

**Security Issues:** Report privately - see [SECURITY.md](SECURITY.md)

### Submitting Pull Requests

1. **Create a feature branch:**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes:**
   - Write clear, commented code
   - Follow existing code style
   - Test your changes locally

3. **Commit with descriptive messages:**
   ```bash
   git commit -m "Add: Feature description"
   ```

4. **Push and create PR:**
   ```bash
   git push origin feature/your-feature-name
   ```
   Then open a Pull Request on GitHub

### Pre-Commit Checklist

Before submitting a PR, verify:

- [ ] Code runs without errors locally
- [ ] No `.env` files or API keys committed
- [ ] No database files (*.db) committed
- [ ] Code follows existing style
- [ ] Comments added for complex logic
- [ ] No hardcoded credentials in source files
- [ ] Updated documentation if needed

## Code Style

- **Python:** Follow PEP 8 guidelines
- **Indentation:** 4 spaces (no tabs)
- **Naming:**
  - Functions: `snake_case`
  - Classes: `PascalCase`
  - Constants: `UPPER_CASE`
- **Comments:** Explain *why*, not *what*
- **Docstrings:** Use for all functions and classes

## Areas for Contribution

### Good First Issues:
- Documentation improvements
- Bug fixes
- UI/UX enhancements
- Adding tests

### Advanced Contributions:
- New API integrations
- Performance optimizations
- Database migrations
- Security improvements

## Testing

Currently, this project does not have automated tests. **Adding tests is a great way to contribute!**

Suggested testing framework: `pytest`

## Documentation

When adding features:
- Update README.md if user-facing
- Add docstrings to functions
- Create markdown docs for complex features
- Update .env.example if new variables added

## Questions?

- Open a GitHub issue for general questions
- Check existing documentation first
- Be respectful and patient

## License

By contributing, you agree that your contributions will be licensed under the GNU General Public License v3.0.

Thank you for contributing! 🎉

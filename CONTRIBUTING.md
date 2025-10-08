# Contributing to Vocalaa

Thank you for your interest in contributing to Vocalaa! We appreciate your time and effort to help improve this project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [How to Contribute](#how-to-contribute)
- [Code Style Guidelines](#code-style-guidelines)
- [Testing](#testing)
- [Pull Request Process](#pull-request-process)
- [Reporting Bugs](#reporting-bugs)
- [Feature Requests](#feature-requests)

## Code of Conduct

Please be respectful and constructive in all interactions. We're committed to providing a welcoming and inclusive environment for all contributors.

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/your-username/vocalaa.git
   cd vocalaa
   ```
3. **Add upstream remote**:
   ```bash
   git remote add upstream https://github.com/original-owner/vocalaa.git
   ```

## Development Setup

Vocalaa is a full-stack application with separate backend and frontend components.

### Prerequisites

**Backend:**
- Python 3.13 or higher
- [uv](https://github.com/astral-sh/uv) package manager (recommended) or pip
- Supabase account (for database)
- Redis instance (for caching)

**Frontend:**
- Node.js 18+ and npm
- Supabase account (for authentication)

### Backend Setup

1. **Navigate to backend directory**:
   ```bash
   cd backend
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   # Using uv (recommended)
   uv pip install -r pyproject.toml

   # Or using pip
   pip install -e .
   ```

4. **Set up environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Run the development server**:
   ```bash
   python -m app.main
   ```

6. **Access the API**:
   - API: http://localhost:8000
   - Docs: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

### Frontend Setup

1. **Navigate to UI directory**:
   ```bash
   cd ui
   ```

2. **Install dependencies**:
   ```bash
   npm install
   ```

3. **Set up environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env with your Supabase configuration
   ```

4. **Run the development server**:
   ```bash
   npm run dev
   ```

5. **Access the application**:
   - Frontend: http://localhost:3000

## How to Contribute

### Types of Contributions

- **Bug fixes** - Fix issues in the codebase
- **New features** - Add new functionality
- **Documentation** - Improve or add documentation
- **Tests** - Add or improve test coverage
- **Code refactoring** - Improve code quality without changing behavior

### Contribution Workflow

1. **Check existing issues** - Look for related issues or create a new one
2. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/bug-description
   ```
3. **Make your changes** - Write code following our style guidelines
4. **Test your changes** - Ensure all tests pass
5. **Commit your changes**:
   ```bash
   git add .
   git commit -m "feat: add feature description"
   ```
6. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```
7. **Open a Pull Request** - Submit PR to the main repository

## Code Style Guidelines

### Backend (Python) Style

- Follow [PEP 8](https://pep8.org/) style guide
- Use type hints for function parameters and return values
- Maximum line length: 100 characters
- Use meaningful variable and function names

**Backend Code Organization:**

```
backend/app/
├── api/routes/      # API endpoints grouped by domain
├── core/            # Core infrastructure (DB, auth, logging, config)
├── models/          # Pydantic models
├── services/        # Business logic
└── utils/           # Utility functions
```

### Frontend (TypeScript/React) Style

- Follow TypeScript and React best practices
- Use functional components with hooks
- Use TypeScript for type safety
- Maximum line length: 100 characters
- Use meaningful variable and function names

**Frontend Code Organization:**

```
ui/src/
├── app/             # Next.js app router pages
├── components/      # Reusable React components
├── lib/             # Utility functions and helpers
└── types/           # TypeScript type definitions
```

### Naming Conventions

**Backend (Python):**
- **Files**: `snake_case.py`
- **Classes**: `PascalCase`
- **Functions/Methods**: `snake_case()`
- **Constants**: `UPPER_SNAKE_CASE`
- **Private methods**: `_leading_underscore()`

**Frontend (TypeScript/React):**
- **Files**: `kebab-case.tsx` or `PascalCase.tsx` (for components)
- **Components**: `PascalCase`
- **Functions/Hooks**: `camelCase`
- **Constants**: `UPPER_SNAKE_CASE`
- **Types/Interfaces**: `PascalCase`

### Example Code

**Backend (Python):**

```python
from typing import Optional
from pydantic import BaseModel
from loguru import logger

class UserProfile(BaseModel):
    """User profile data model."""
    name: str
    email: str
    bio: Optional[str] = None

async def create_user_profile(profile_data: UserProfile) -> dict:
    """
    Create a new user profile.

    Args:
        profile_data: User profile information

    Returns:
        Created profile with ID and timestamps

    Raises:
        HTTPException: If profile creation fails
    """
    logger.info(f"Creating profile for: {profile_data.email}")
    # Implementation here
    return {"id": "123", "status": "created"}
```

**Frontend (TypeScript/React):**

```typescript
import { useState } from 'react';

interface UserProfileProps {
  name: string;
  email: string;
  bio?: string;
}

export function UserProfileCard({ name, email, bio }: UserProfileProps) {
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async () => {
    setIsLoading(true);
    try {
      // Implementation here
      console.log('Profile submitted');
    } catch (error) {
      console.error('Error submitting profile:', error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="profile-card">
      <h2>{name}</h2>
      <p>{email}</p>
      {bio && <p>{bio}</p>}
    </div>
  );
}
```

## Testing

### Backend Testing

**Running Tests:**

```bash
cd backend

# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_auth.py

# Run with coverage
pytest --cov=app tests/
```

**Writing Tests:**

- Place tests in the `backend/tests/` directory
- Name test files: `test_*.py`
- Name test functions: `test_*`
- Use descriptive test names that explain what is being tested
- Use fixtures from `conftest.py` for common setup

Example test:
```python
def test_user_registration(client, test_user_data):
    """Test successful user registration."""
    response = client.post("/auth/register", json=test_user_data)
    assert response.status_code == 200
    assert "user_id" in response.json()
```

### Frontend Testing

**Running Tests:**

```bash
cd ui

# Run all tests
npm test

# Run tests in watch mode
npm test -- --watch

# Run with coverage
npm test -- --coverage
```

**Writing Tests:**

- Place tests in the `ui/src/__tests__/` directory or alongside components
- Use Jest and React Testing Library
- Test component behavior, not implementation details
- Mock API calls and external dependencies

### Test Coverage

- Aim for **80%+ code coverage** for both backend and frontend
- Test happy paths and edge cases
- Test error handling
- Mock external services (Supabase, Redis, API calls)

## Pull Request Process

### Before Submitting

- [ ] Code follows the style guidelines
- [ ] All tests pass locally
- [ ] Added tests for new features
- [ ] Updated documentation if needed
- [ ] No commented-out code or debug prints
- [ ] Commit messages are clear and descriptive

### PR Guidelines

1. **Title**: Use conventional commit format
   - `feat: add user profile export`
   - `fix: resolve caching issue in MCP endpoints`
   - `docs: update API documentation`
   - `test: add tests for authentication`
   - `refactor: improve database connection pooling`

2. **Description**: Provide context
   - What problem does this solve?
   - What changes were made?
   - How was it tested?
   - Any breaking changes?

3. **Link related issues**: Reference issue numbers (e.g., "Fixes #123")

4. **Keep PRs focused**: One feature or fix per PR

5. **Respond to feedback**: Address review comments promptly

### Review Process

- At least one maintainer approval required
- All CI checks must pass
- No merge conflicts
- Maintainers may request changes or improvements

## Reporting Bugs

### Before Reporting

- Check if the bug has already been reported
- Verify it's reproducible on the latest version
- Gather relevant information

### Bug Report Template

```markdown
**Describe the bug**
A clear description of what the bug is.

**To Reproduce**
Steps to reproduce the behavior:
1. Call endpoint '...'
2. With payload '...'
3. See error

**Expected behavior**
What you expected to happen.

**Actual behavior**
What actually happened.

**Environment**
- Python version:
- FastAPI version:
- OS:

**Logs**
```
Paste relevant logs here
```

**Additional context**
Any other context about the problem.
```

## Feature Requests

We welcome feature requests! Please:

1. **Check existing requests** - Avoid duplicates
2. **Be specific** - Clearly describe the feature
3. **Explain the use case** - Why is this needed?
4. **Consider scope** - Keep it focused and achievable

### Feature Request Template

```markdown
**Feature description**
Clear description of the feature.

**Use case**
Why is this feature needed? What problem does it solve?

**Proposed solution**
How would you implement this?

**Alternatives considered**
What other solutions did you consider?

**Additional context**
Any other relevant information.
```

## Questions?

- Open an issue with the "question" label
- Check existing discussions
- Review the documentation

## License

By contributing, you agree that your contributions will be licensed under the same license as the project.

---

Thank you for contributing to Vocalaa! 🎉

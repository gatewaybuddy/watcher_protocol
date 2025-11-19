# Contributing to Watcher Protocol

Thank you for your interest in contributing to Watcher Protocol! This document provides guidelines and instructions for contributing.

## Code of Conduct

- Be respectful and inclusive
- Welcome newcomers
- Focus on constructive feedback
- Prioritize AI safety and alignment goals

## How to Contribute

### Reporting Issues

1. Check existing issues first
2. Use issue templates
3. Provide detailed reproduction steps
4. Include system information and logs

### Suggesting Features

1. Open a discussion first for major features
2. Explain the use case and benefits
3. Consider alignment with project goals
4. Be open to feedback and alternative approaches

### Submitting Pull Requests

1. **Fork and clone**
   ```bash
   git clone https://github.com/YOUR_USERNAME/watcher_protocol.git
   cd watcher_protocol
   ```

2. **Create a branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make changes**
   - Follow code style guidelines
   - Add tests
   - Update documentation
   - Keep commits focused and atomic

4. **Test your changes**
   ```bash
   # Backend tests
   cd backend
   pytest

   # Frontend tests
   cd frontend
   npm test

   # Linting
   black backend/
   ruff backend/
   npm run lint
   ```

5. **Commit with clear messages**
   ```bash
   git commit -m "Add semantic search for alignment papers"
   ```

6. **Push and create PR**
   ```bash
   git push origin feature/your-feature-name
   ```

## Development Setup

See README.md for detailed setup instructions.

## Code Style

### Python (Backend)

- Follow PEP 8
- Use `black` for formatting
- Use `ruff` for linting
- Type hints required
- Docstrings for public functions

```python
async def fetch_items(
    category: Optional[str] = None,
    limit: int = 20
) -> List[Item]:
    """
    Fetch items from database.

    Args:
        category: Filter by category
        limit: Maximum number of items

    Returns:
        List of Item objects
    """
    pass
```

### TypeScript (Frontend)

- Use TypeScript strict mode
- ESLint for linting
- Prettier for formatting
- Functional components with hooks
- Props interfaces required

```typescript
interface ItemCardProps {
  item: Item;
  onClick?: () => void;
}

export function ItemCard({ item, onClick }: ItemCardProps) {
  // Component implementation
}
```

## Testing

### Backend Tests

```python
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_list_items():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/v1/items")
        assert response.status_code == 200
```

### Frontend Tests

```typescript
import { render, screen } from '@testing-library/react';
import { Dashboard } from './Dashboard';

test('renders dashboard', () => {
  render(<Dashboard />);
  expect(screen.getByText('Watcher Protocol')).toBeInTheDocument();
});
```

## Documentation

- Update README.md for user-facing changes
- Update ARCHITECTURE.md for technical changes
- Add inline comments for complex logic
- Update API documentation

## Adding Data Sources

To add a new scraper:

1. Create scraper class in `backend/utils/scrapers/`
2. Inherit from `BaseScraper`
3. Implement `fetch()` and `parse()` methods
4. Add configuration to `config.py`
5. Register in scheduler
6. Add tests
7. Document in README

Example:

```python
class NewScraper(BaseScraper):
    async def fetch(self) -> List[Any]:
        # Fetch data from source
        pass

    async def parse(self, raw_data: List[Any]) -> List[ParsedItem]:
        # Parse into standardized format
        pass
```

## Commit Message Guidelines

Format: `<type>: <description>`

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Formatting
- `refactor`: Code restructuring
- `test`: Adding tests
- `chore`: Maintenance

Examples:
```
feat: add GitHub repository monitoring
fix: handle arxiv rate limiting correctly
docs: update deployment guide for AWS
```

## Review Process

1. CI checks must pass
2. At least one maintainer review
3. All comments addressed
4. Up to date with main branch
5. Documentation updated

## Areas Needing Help

- **Data Sources**: Integrating new sources
- **ML Models**: Improving classification
- **Frontend**: UI/UX improvements
- **Documentation**: Examples and tutorials
- **Testing**: Increasing coverage
- **Performance**: Optimization

## Questions?

- Open a discussion on GitHub
- Join our community chat
- Email: contributors@watcherprotocol.com

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

## Recognition

Contributors will be acknowledged in:
- README.md
- Release notes
- Project website

Thank you for helping make AI safer! 🦇

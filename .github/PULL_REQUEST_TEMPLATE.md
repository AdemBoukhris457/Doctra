# Pull Request

## Description

<!-- Provide a brief description of the changes in this PR -->

## Type of Change

Please delete options that are not relevant.

- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update
- [ ] Performance improvement
- [ ] Code refactoring
- [ ] Test addition/update
- [ ] Dependencies update

## Related Issues

<!-- Link to any related issues using "Fixes #123" or "Closes #123" -->
<!-- Use "Fixes #123" for bug fixes and "Closes #123" for feature requests -->
<!-- Multiple issues can be referenced: "Fixes #123, #456" -->

Fixes #

**Important**: Please mention all related issues that this PR addresses. Use the following keywords:
- `Fixes #123` - for bug fixes
- `Closes #123` - for feature requests or general issues
- `Resolves #123` - alternative to Closes
- `Addresses #123` - for partial fixes or related work

## Changes Made

<!-- List the main changes made in this PR -->

- 
- 
- 

## Testing

### Test Coverage

- [ ] All existing tests pass
- [ ] New tests added for new functionality
- [ ] Test coverage maintained or improved
- [ ] Manual testing completed

### Test Commands

```bash
# Run all tests
pytest

# Run specific tests (if applicable)
pytest tests/test_specific_module.py

# Run with coverage
pytest --cov=doctra --cov-report=html
```

### Manual Testing

<!-- Describe any manual testing performed -->

- [ ] Tested with sample PDFs
- [ ] Tested CLI functionality (if applicable)
- [ ] Tested web UI (if applicable)
- [ ] Tested with different file types
- [ ] Tested error handling

## Code Quality

### Code Style

- [ ] Code follows the project's style guidelines
- [ ] Black formatting applied: `black doctra tests`
- [ ] Import sorting applied: `isort doctra tests`
- [ ] No linting errors: `flake8 doctra tests`
- [ ] Type hints added where appropriate
- [ ] Docstrings follow the project's format

### Code Review Checklist

- [ ] Code is readable and well-documented
- [ ] Functions and classes have appropriate docstrings
- [ ] No hardcoded values or magic numbers
- [ ] Error handling is implemented
- [ ] No unused imports or variables
- [ ] Code follows DRY principles

## Documentation

### Documentation Updates

- [ ] README.md updated (if applicable)
- [ ] API documentation updated
- [ ] User guide updated (if applicable)
- [ ] Code comments added where necessary
- [ ] CHANGELOG.md updated (if applicable)

### Documentation Commands

```bash
# Build documentation locally (if applicable)
mkdocs serve
```

## Performance

### Performance Considerations

- [ ] No significant performance regression
- [ ] Memory usage optimized (if applicable)
- [ ] Large file handling tested
- [ ] API rate limits considered

## Security

### Security Considerations

- [ ] No sensitive data exposed
- [ ] Input validation implemented
- [ ] File handling is secure
- [ ] API keys handled securely
- [ ] No security vulnerabilities introduced

## Breaking Changes

<!-- If this is a breaking change, describe what breaks and how to migrate -->

### Breaking Changes

- [ ] No breaking changes
- [ ] Breaking changes documented below

<!-- If breaking changes exist, describe them here -->

## Screenshots/Examples

<!-- If applicable, add screenshots or examples of the changes -->

### Before
<!-- Screenshot or description of before state -->

### After
<!-- Screenshot or description of after state -->

## Additional Notes

<!-- Any additional information that reviewers should know -->

## Checklist

### Pre-submission Checklist

- [ ] All tests pass locally
- [ ] Code is formatted and linted
- [ ] Documentation is updated
- [ ] Breaking changes are documented
- [ ] Security considerations addressed
- [ ] Performance impact assessed
- [ ] PR description is complete
- [ ] Related issues are linked

### Reviewer Checklist

- [ ] Code quality is acceptable
- [ ] Tests are comprehensive
- [ ] Documentation is clear
- [ ] No security issues
- [ ] Performance is acceptable
- [ ] Breaking changes are justified

## Dependencies

### New Dependencies

<!-- List any new dependencies added -->

- 

### Updated Dependencies

<!-- List any dependencies that were updated -->

- 

### Dependency Impact

- [ ] No new dependencies added
- [ ] New dependencies are justified and documented
- [ ] Dependencies are compatible with existing versions
- [ ] Security implications of new dependencies considered

## Deployment

### Deployment Considerations

- [ ] No special deployment steps required
- [ ] Database migrations required (if applicable)
- [ ] Configuration changes required
- [ ] Environment variables need to be updated

## Rollback Plan

<!-- Describe how to rollback this change if needed -->

## Related PRs

<!-- Link to any related PRs -->

## Reviewer Assignment

<!-- Tag specific reviewers if needed -->

@AdemBoukhris457

---

**Note**: Please ensure all checkboxes are completed before submitting the PR. This helps maintain code quality and ensures thorough review.

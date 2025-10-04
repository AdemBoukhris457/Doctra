# Security Policy

## Supported Versions

We actively support the following versions of Doctra with security updates:

| Version | Supported          |
| ------- | ------------------ |
| 0.5.x   | :white_check_mark: |
| 0.4.x   | :white_check_mark: |
| < 0.4   | :x:                |

## Reporting a Vulnerability

We take security vulnerabilities seriously. If you discover a security vulnerability in Doctra, please report it responsibly.

### How to Report

**Please do NOT report security vulnerabilities through public GitHub issues.**

Instead, please report them privately by emailing:

**boukhrisadam98@gmail.com**

### What to Include

When reporting a security vulnerability, please include:

- **Description**: A clear description of the vulnerability
- **Steps to Reproduce**: Detailed steps to reproduce the issue
- **Impact**: Potential impact and severity assessment
- **Affected Versions**: Which versions are affected
- **Proof of Concept**: If applicable, include a minimal proof of concept
- **Suggested Fix**: If you have ideas for fixing the issue

### Response Timeline

- **Acknowledgment**: We will acknowledge receipt within 48 hours
- **Initial Assessment**: We will provide an initial assessment within 5 business days
- **Resolution**: We will work to resolve critical vulnerabilities within 30 days
- **Updates**: We will provide regular updates on our progress

### What to Expect

1. **Confirmation**: We will confirm receipt of your report
2. **Investigation**: We will investigate the reported vulnerability
3. **Fix Development**: We will develop and test a fix
4. **Release**: We will release a security update
5. **Credit**: We will credit you in our security advisories (unless you prefer to remain anonymous)

## Security Best Practices

### For Users

When using Doctra, please follow these security best practices:

#### API Keys and Credentials

- **Never commit API keys** to version control
- **Use environment variables** for sensitive configuration:
  ```python
  import os
  
  # Good
  api_key = os.getenv('OPENAI_API_KEY')
  
  # Bad - never do this
  api_key = "sk-your-actual-api-key-here"
  ```
- **Rotate API keys regularly**
- **Use least-privilege access** for API keys

#### File Handling

- **Validate input files** before processing
- **Be cautious with untrusted PDFs** - they may contain malicious content
- **Use sandboxed environments** for processing unknown documents
- **Clean up temporary files** after processing

#### Network Security

- **Use HTTPS** for all API communications
- **Verify SSL certificates** when making API calls
- **Consider using VPNs** for sensitive document processing

### For Developers

#### Code Security

- **Validate all inputs** thoroughly
- **Use parameterized queries** for database operations
- **Sanitize user inputs** before processing
- **Implement proper error handling** without exposing sensitive information

#### Dependencies

- **Keep dependencies updated** regularly
- **Use dependency scanning tools** to identify vulnerabilities
- **Review dependency licenses** for compatibility

#### File Processing

- **Implement file size limits** to prevent DoS attacks
- **Validate file types** before processing
- **Use secure temporary directories** for file operations
- **Clean up resources** properly

## Security Considerations

### Document Processing

Doctra processes various document types, which presents unique security considerations:

#### PDF Security

- **Malicious PDFs**: PDFs can contain embedded JavaScript or other executable content
- **Metadata**: PDFs may contain sensitive metadata
- **File Size**: Large files can cause memory issues

#### Image Processing

- **Image-based attacks**: Malicious images can exploit image processing libraries
- **Memory consumption**: Large images can cause out-of-memory errors
- **Format validation**: Ensure images are in expected formats

#### API Security

- **Rate limiting**: Implement rate limiting for API calls
- **Authentication**: Use proper authentication for API services
- **Data transmission**: Ensure sensitive data is encrypted in transit

### Recommended Security Measures

#### Environment Setup

```python
# Use environment variables for sensitive data
import os
from pathlib import Path

# Secure configuration
API_KEY = os.getenv('VLM_API_KEY')
TEMP_DIR = Path(os.getenv('TEMP_DIR', '/tmp/doctra'))
MAX_FILE_SIZE = int(os.getenv('MAX_FILE_SIZE', '100MB'))
```

#### Input Validation

```python
def validate_pdf_file(file_path: str) -> bool:
    """Validate PDF file for security."""
    # Check file size
    if os.path.getsize(file_path) > MAX_FILE_SIZE:
        raise ValueError("File too large")
    
    # Check file type
    if not file_path.lower().endswith('.pdf'):
        raise ValueError("Invalid file type")
    
    # Additional validation...
    return True
```

#### Safe File Operations

```python
import tempfile
import shutil
from pathlib import Path

def safe_process_pdf(pdf_path: str):
    """Process PDF in a secure manner."""
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir) / "input.pdf"
        shutil.copy2(pdf_path, temp_path)
        
        try:
            # Process the file
            result = process_file(temp_path)
            return result
        finally:
            # Cleanup is automatic with TemporaryDirectory
            pass
```

## Security Updates

### How We Handle Security Updates

1. **Immediate Response**: Critical vulnerabilities receive immediate attention
2. **Patch Development**: We develop and test security patches
3. **Release Process**: Security updates are released as soon as possible
4. **Communication**: We communicate security updates through:
   - GitHub releases
   - Security advisories
   - Email notifications (for critical issues)

### Staying Updated

To stay informed about security updates:

- **Watch the repository** for security-related releases
- **Subscribe to notifications** for security advisories
- **Follow our documentation** for security best practices
- **Update regularly** to the latest version

## Security Tools and Resources

### Recommended Tools

- **Dependency Scanning**: Use tools like `safety` or `pip-audit`
- **Code Analysis**: Use tools like `bandit` for Python security analysis
- **File Validation**: Validate file types and sizes before processing

### Example Security Checks

```bash
# Check for known vulnerabilities in dependencies
pip install safety
safety check

# Analyze code for security issues
pip install bandit
bandit -r doctra/

# Audit dependencies
pip install pip-audit
pip-audit
```

## Contact Information

For security-related questions or concerns:

- **Email**: boukhrisadam98@gmail.com
- **GitHub**: [AdemBoukhris457](https://github.com/AdemBoukhris457)
- **Issues**: Use GitHub Issues for non-security related questions

## Acknowledgments

We appreciate the security researchers and community members who help keep Doctra secure by responsibly reporting vulnerabilities.

## License

This security policy is part of the Doctra project and is subject to the same Apache License 2.0 terms as the main project.

# Unit Tests for vMotion Application Notification

This directory contains comprehensive unit tests for the vMotion Application Notification service.

## Test Files

- **test_vmnotification_config.py** - Tests for VMNotificationConfig class
- **test_vmnotification_service.py** - Tests for VMNotificationService class
- **test_utils.py** - Tests for utility functions
- **test_vmnotification_exception.py** - Tests for VMNotificationException class
- **test_all.py** - Test runner for all tests
- **__init__.py** - Package initialization

## Running Tests

### Run All Tests (from project root)
```bash
# Using the convenience script
python3 run_tests.py

# Or directly
python3 tests/test_all.py

# Or using unittest discovery
python3 -m unittest discover tests
```

### Run All Tests (Verbose)
```bash
python3 run_tests.py -v
```

### Run All Tests (Quiet)
```bash
python3 run_tests.py -q
```

### Run Individual Test Files
```bash
# Test configuration
python3 -m unittest tests.test_vmnotification_config

# Test service
python3 -m unittest tests.test_vmnotification_service

# Test utilities
python3 -m unittest tests.test_utils

# Test exception
python3 -m unittest tests.test_vmnotification_exception
```

### Run Specific Test Class
```bash
python3 -m unittest tests.test_vmnotification_config.TestVMNotificationConfig
```

### Run Specific Test Method
```bash
python3 -m unittest tests.test_vmnotification_config.TestVMNotificationConfig.test_config_file_loading
```

## Test Coverage

### VMNotificationConfig Tests (30+ tests)
- Configuration file loading
- Default values
- Property validation (all properties)
- Type checking
- Error messages
- JSON serialization

### VMNotificationService Tests (25+ tests)
- Service initialization
- Command splitting
- Token management (read, write, delete)
- Message obfuscation
- RPC calls (success and failure)
- Registration/unregistration
- Event acknowledgment
- Pre/post vMotion command execution
- Signal handling
- Integration tests

### Utils Tests (15+ tests)
- Logging level conversion
- Folder creation
- Path handling
- Permission errors
- Edge cases

### VMNotificationException Tests (7+ tests)
- Exception creation
- Inheritance
- Error handling
- Special characters

## Test Requirements

The tests use only Python standard library modules:
- `unittest` - Test framework
- `unittest.mock` - Mocking support
- `tempfile` - Temporary file/directory creation
- `os` - Operating system interface
- `pathlib` - Path operations
- `json` - JSON handling

No additional dependencies required!

## Test Structure

Each test file follows this structure:
1. **Setup** - Create test fixtures (temp files, mock objects)
2. **Test Execution** - Run the test
3. **Assertions** - Verify expected behavior
4. **Teardown** - Clean up test fixtures

## Writing New Tests

To add new tests:

1. Create a new test class inheriting from `unittest.TestCase`
2. Add `setUp()` method for test fixtures
3. Add `tearDown()` method for cleanup
4. Write test methods starting with `test_`
5. Add the test class to `test_all.py`

Example:
```python
class TestNewFeature(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures"""
        self.test_data = "test"
    
    def tearDown(self):
        """Clean up"""
        pass
    
    def test_feature(self):
        """Test the new feature"""
        result = my_function(self.test_data)
        self.assertEqual(result, expected_value)
```

## Continuous Integration

These tests can be integrated into CI/CD pipelines:

```bash
# Run tests and exit with appropriate code
python3 test_all.py
if [ $? -eq 0 ]; then
    echo "All tests passed!"
else
    echo "Tests failed!"
    exit 1
fi
```

## Test Best Practices

1. **Isolation** - Each test should be independent
2. **Cleanup** - Always clean up test artifacts
3. **Clear Names** - Test names should describe what they test
4. **One Assertion** - Focus each test on one behavior
5. **Mock External Dependencies** - Use mocks for external services
6. **Fast Execution** - Tests should run quickly

## Troubleshooting

### Permission Errors
Some tests may fail if run without appropriate permissions. These tests are designed to handle permission errors gracefully.

### Temporary Files
Tests create temporary files/directories that are automatically cleaned up. If cleanup fails, check `/tmp` for leftover test files.

### Mock Issues
If mocking tests fail, ensure you're using Python 3.3+ which includes `unittest.mock` in the standard library.

## Coverage Report

To generate a coverage report (requires `coverage` package):

```bash
# Install coverage
pip install coverage

# Run tests with coverage
coverage run -m unittest discover

# Generate report
coverage report -m

# Generate HTML report
coverage html
```

## Contributing

When adding new features:
1. Write tests first (TDD approach)
2. Ensure all tests pass
3. Maintain test coverage above 80%
4. Update this README if needed


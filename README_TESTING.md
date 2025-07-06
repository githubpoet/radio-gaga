# Radio Gaga Test Suite

This document describes the automated test suite for Radio Gaga, covering configuration resolution, default file creation, and CLI functionality.

## Test Overview

The test suite includes comprehensive testing for:

- **Configuration Path Resolution**: Tests the priority order of config file discovery
- **Environment Variable Overrides**: Tests RADIO_GAGA_CONFIG environment variable functionality
- **Default File Creation**: Tests automatic creation of user configuration on first run
- **CLI Functionality**: Functional tests of the radio-gaga CLI with temporary configurations
- **Platform-Specific Behavior**: Tests macOS and Linux configuration directory resolution
- **Error Handling**: Tests proper error handling for invalid configs and missing files

## Test Files

### `test_config_resolution.py`
Comprehensive unit tests covering:
- `get_config_path()` resolution order with `tmp_path` fixtures
- Environment variable overrides with isolated test environments  
- Default file creation scenarios
- Configuration file loading and validation
- Platform-specific directory resolution
- Error handling for missing/invalid configs

### `test_cli_functional.py`
Functional CLI tests covering:
- `radio-gaga --config tmp.yaml --cli` functionality
- Station list loading from temporary YAML/JSON configs
- Error handling for nonexistent and invalid configuration files
- Play mode with temporary configurations
- Config info display functionality

### `test_template_config.py` (Legacy)
Existing test for template configuration functionality.

## Running the Tests

### Prerequisites

Install test dependencies:
```bash
pip install -r requirements-test.txt
```

Or install individual packages:
```bash
pip install pytest pytest-cov pytest-mock PyYAML
```

### Run All Tests

```bash
# Run all tests with verbose output
python3 -m pytest test_config_resolution.py test_cli_functional.py -v

# Run tests with coverage
python3 -m pytest test_config_resolution.py test_cli_functional.py --cov=config --cov-report=term-missing

# Run tests with short output
python3 -m pytest test_config_resolution.py test_cli_functional.py --tb=short
```

### Run Specific Test Categories

```bash
# Configuration resolution tests only
python3 -m pytest test_config_resolution.py::TestGetConfigPathResolution -v

# Default file creation tests only  
python3 -m pytest test_config_resolution.py::TestDefaultFileCreation -v

# CLI functional tests only
python3 -m pytest test_cli_functional.py -v

# Platform-specific tests only
python3 -m pytest test_config_resolution.py::TestPlatformSpecific -v
```

### Run Individual Tests

```bash
# Test CLI argument priority
python3 -m pytest test_config_resolution.py::TestGetConfigPathResolution::test_cli_arg_highest_priority -v

# Test environment variable overrides
python3 -m pytest test_config_resolution.py::TestGetConfigPathResolution::test_environment_overrides -v

# Test CLI with YAML config
python3 -m pytest test_cli_functional.py::TestCLIFunctional::test_radio_gaga_cli_with_yaml_config -v

# Test first-run scenario  
python3 -m pytest test_config_resolution.py::TestDefaultFileCreation::test_first_run_integration -v
```

## Test Configuration

### pytest.ini
The project includes a `pytest.ini` file with standard configuration:
- Test discovery patterns
- Output formatting options  
- Coverage settings
- Test markers for categorization

### Test Markers

Tests are categorized with markers:
- `unit`: Unit tests for individual functions
- `integration`: Integration tests across components
- `cli`: CLI functionality tests
- `config`: Configuration-related tests

Use markers to run specific test categories:
```bash
# Run only unit tests (when marked)
python3 -m pytest -m unit

# Run only CLI tests (when marked) 
python3 -m pytest -m cli
```

## CI/CD Integration

### GitHub Actions Workflow

The project includes a comprehensive GitHub Actions workflow (`.github/workflows/test.yml`) that:

- Runs tests on both **Ubuntu** and **macOS**
- Tests multiple Python versions (3.8-3.12)
- Installs platform-specific system dependencies
- Runs the complete test suite
- Generates coverage reports
- Includes integration testing with real config files
- Tests error handling scenarios

### Workflow Jobs

1. **test**: Main test job with matrix strategy for OS and Python versions
2. **integration-test**: Additional integration testing with config file scenarios  
3. **lint-and-format**: Code quality checks with flake8, black, isort, mypy

### Running CI Locally

To simulate CI environment locally:

```bash
# Install test dependencies
pip install -r requirements-test.txt

# Run the same tests as CI
python3 -m pytest test_config_resolution.py test_cli_functional.py -v --tb=short

# Run legacy tests
python3 test_template_config.py

# Test CLI functionality
python3 radio.py --cli
python3 config.py --info
```

## Test Coverage

The test suite provides comprehensive coverage of:

- ✅ **Config Resolution Priority Order**: CLI arg → ENV var → Platform dir → Legacy → Packaged
- ✅ **Environment Variable Handling**: RADIO_GAGA_CONFIG override scenarios
- ✅ **First-Run Behavior**: Automatic user config creation
- ✅ **File Format Support**: YAML and JSON configuration loading
- ✅ **Platform Compatibility**: macOS and Linux directory resolution
- ✅ **Error Handling**: Invalid configs, missing files, permission errors
- ✅ **CLI Integration**: Functional testing with `radio-gaga --config tmp.yaml`
- ✅ **Cross-Platform Testing**: Tests run on both macOS and Linux in CI

## Expected Test Results

All tests should pass on both macOS and Linux platforms:

```
============================= test session starts ==============================
collected 35 items

test_config_resolution.py::TestGetConfigPathResolution::test_cli_arg_highest_priority PASSED
test_config_resolution.py::TestGetConfigPathResolution::test_environment_variable_second_priority PASSED
[... 33 more tests ...]
test_cli_functional.py::TestCLIFunctional::test_radio_gaga_config_info_display PASSED

============================== 35 passed in XX.XXs ==============================
```

## Troubleshooting

### Common Issues

1. **ImportError for config module**: Ensure you're running tests from the project root directory
2. **PyYAML not available**: Install with `pip install PyYAML`
3. **Permission errors**: Some tests create temporary directories with restricted permissions
4. **Timeout in CLI tests**: CLI tests may timeout on slower systems; this is handled gracefully

### Debug Mode

Run tests with more verbose output:
```bash
python3 -m pytest test_config_resolution.py -v -s --tb=long
```

### Environment Isolation

Tests use `tmp_path` fixtures and environment mocking to ensure isolation. Each test runs in a clean environment without affecting system configuration files.

## Contributing

When adding new tests:

1. Use descriptive test names following the pattern `test_<functionality>_<scenario>`
2. Include docstrings explaining what each test validates
3. Use `tmp_path` fixtures for file operations
4. Mock external dependencies and system paths
5. Test both success and error scenarios
6. Add appropriate test markers
7. Ensure tests pass on both macOS and Linux

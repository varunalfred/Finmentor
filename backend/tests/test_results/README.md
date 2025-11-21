# Test Results Directory

This directory contains automated test results from the individual agent testing suite.

## File Types

### Log Files (`.log`)
- **Format**: Plain text with UTF-8 encoding
- **Naming**: `individual_agents_YYYYMMDD_HHMMSS.log`
- **Content**: Complete test run output including:
  - Test start/end timestamps
  - Individual agent test results
  - Detailed validation results
  - Summary statistics
  - Failed test details with error messages

### JSON Files (`.json`)
- **Format**: Structured JSON data
- **Naming**: `individual_agents_YYYYMMDD_HHMMSS.json`
- **Content**: Machine-readable test results for programmatic analysis
  - Test suite metadata
  - Overall statistics (success rate, counts)
  - Detailed results for each agent including:
    - Success status
    - Keywords found/missing
    - Match rate
    - Knowledge base usage
    - Sources used
    - Timing information
    - Error messages (if any)

## Usage

### Viewing Logs
Open `.log` files in any text editor to review complete test output.

### Analyzing Results Programmatically
```python
import json

# Load test results
with open('test_results/individual_agents_20251112_225045.json', 'r') as f:
    results = json.load(f)

# Access summary
print(f"Success Rate: {results['success_rate']}%")
print(f"Total Agents: {results['total_agents']}")

# Analyze individual results
for agent_result in results['results']:
    if not agent_result['success']:
        print(f"Failed: {agent_result['agent']}")
        print(f"  Missing: {agent_result.get('keywords_missing', [])}")
```

## Retention

Test results are automatically timestamped and retained indefinitely for analysis and comparison. You may manually delete old results if needed.

## .gitignore

This directory is typically excluded from git to avoid cluttering the repository with test output. Only the README is tracked.

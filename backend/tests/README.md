# Observability & Metrics Test Suite

Comprehensive test suite for the MCP observability and metrics tracking system.

## Test Files

### 1. `test_observability.py`
Unit tests for the core observability module (`app/core/observability.py`).

**Tests:**
- ToolMetrics and PerformanceMetrics data classes
- MetricsCollector functionality
- Tool call recording and statistics
- User activity tracking
- Performance summary generation
- Error tracking and summarization
- Time-based filtering
- Metrics cleanup
- `@track_performance` decorator
- `record_tool_call()` helper function

**Run:**
```bash
pytest tests/test_observability.py -v
```

### 2. `test_metrics_endpoints.py`
Integration tests for the metrics API endpoints (`app/api/routes/metrics.py`).

**Tests:**
- Authentication requirements
- `/metrics/tools` - Tool usage statistics
- `/metrics/users` - User activity statistics
- `/metrics/performance` - Performance summaries
- `/metrics/errors` - Error summaries
- `/metrics/dashboard` - Comprehensive dashboard
- `/metrics/clear` - Metrics cleanup
- Parameter validation (hours parameter)
- Edge cases and error handling
- Concurrent request handling

**Run:**
```bash
pytest tests/test_metrics_endpoints.py -v
```

### 3. `test_mcp_observability.py`
Integration tests for MCP service with observability (`app/services/mcp_service.py`).

**Tests:**
- Tool call metrics recording
- Multiple tool call tracking
- Failed tool call tracking
- Duration tracking
- Request ID tracking
- Timestamp recording
- Metrics API integration
- User activity tracking
- Complete workflow testing
- Error tracking workflow

**Run:**
```bash
pytest tests/test_mcp_observability.py -v
```

## Running Tests

### Run All Observability Tests
```bash
pytest tests/test_observability.py tests/test_metrics_endpoints.py tests/test_mcp_observability.py -v
```

### Run All Tests (including existing tests)
```bash
pytest tests/ -v
```

### Run with Coverage
```bash
pytest tests/ --cov=app.core.observability --cov=app.api.routes.metrics --cov-report=html
```

### Run Specific Test Class
```bash
pytest tests/test_observability.py::TestMetricsCollector -v
```

### Run Specific Test
```bash
pytest tests/test_metrics_endpoints.py::TestToolsEndpoint::test_get_tool_statistics_with_auth -v
```

## Test Fixtures

Available fixtures in `conftest.py`:

- `client` - FastAPI TestClient
- `supabase_client` - Supabase client instance
- `test_user_data` - Sample user registration data
- `metrics_collector` - MetricsCollector instance
- `clear_metrics` - Clears all metrics before test
- `auth_token` - Valid JWT authentication token
- `auth_headers` - Authorization headers with token

## Test Coverage

The test suite covers:

### Core Functionality
- ✅ Metrics collection and storage
- ✅ Tool call tracking (success & failures)
- ✅ Performance measurement
- ✅ User activity monitoring
- ✅ Error tracking and reporting
- ✅ Time-based filtering
- ✅ Statistics aggregation

### API Endpoints
- ✅ Authentication & authorization
- ✅ All metrics endpoints
- ✅ Parameter validation
- ✅ Error handling
- ✅ Response structure validation

### Integration
- ✅ MCP tool calls with metrics
- ✅ End-to-end workflows
- ✅ Multi-user scenarios
- ✅ Concurrent operations

## Test Data Cleanup

Most tests use unique identifiers (UUID) to avoid conflicts. The `clear_metrics` fixture can be used to ensure a clean state:

```python
def test_with_clean_metrics(client, clear_metrics):
    # Metrics are cleared before this test runs
    ...
```

## Continuous Integration

To run tests in CI/CD:

```yaml
# Example GitHub Actions
- name: Run tests
  run: |
    pytest tests/ -v --cov=app --cov-report=xml

- name: Upload coverage
  uses: codecov/codecov-action@v3
  with:
    files: ./coverage.xml
```

## Troubleshooting

### Issue: Tests failing due to existing metrics

**Solution:** Use the `clear_metrics` fixture or clear metrics manually:
```python
from app.core.observability import get_metrics_collector
collector = get_metrics_collector()
collector.clear_old_metrics(hours=0)
```

### Issue: Authentication failures

**Solution:** Ensure Supabase is configured correctly and the test database is accessible.

### Issue: Concurrent test failures

**Solution:** The MetricsCollector is a singleton, so concurrent tests may interfere. Consider:
- Running tests sequentially: `pytest -n 1`
- Using test isolation strategies
- Clearing metrics between tests

## Best Practices

1. **Use fixtures** - Leverage existing fixtures for common setup
2. **Unique identifiers** - Use UUID for test data to avoid conflicts
3. **Clean up** - Clear metrics after tests that populate data
4. **Test isolation** - Don't rely on data from other tests
5. **Descriptive names** - Use clear, descriptive test names
6. **Assert clearly** - Make assertions specific and meaningful

## Example Test

```python
def test_tool_call_metrics(client, auth_headers, clear_metrics):
    """Test that tool calls are properly tracked"""
    collector = get_metrics_collector()

    # Make MCP tool call
    response = client.post("/mcp/test-user", json={
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {"name": "get_basic_info"}
    })

    assert response.status_code == 200

    # Verify metrics recorded
    stats = collector.get_tool_statistics(hours=1)
    assert stats["total_calls"] >= 1
```

## Additional Resources

- [FastAPI Testing Documentation](https://fastapi.tiangolo.com/tutorial/testing/)
- [Pytest Documentation](https://docs.pytest.org/)
- [Test Coverage Guide](https://coverage.readthedocs.io/)

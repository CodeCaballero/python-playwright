import pytest

def test_transactions(api_client_with_auth):
    response = api_client_with_auth.transactions()
    assert response.status == 200
    data = response.json()
    page_data = data.get('pageData')
    assert page_data is not None, "Missing 'pageData' in response"
    assert page_data['page'] == 1, "Default page should be 1"
    assert page_data['limit'] == 10, "Default limit should be 10"
    assert page_data['totalPages'] > 0, "Should have at least 1 page"

    results = data.get('results')
    assert isinstance(results, list), "'results' should be a list"
    assert len(results) == 10, f"Expected 10 transactions per page, got {len(results)}"

    if results:
        first_txn = results[0]
        assert 'id' in first_txn, "Transaction missing 'id'"
        assert 'amount' in first_txn, "Transaction missing 'amount'"
        assert isinstance(first_txn['amount'], int), "'amount' should be an integer"
        assert 'status' in first_txn, "Transaction missing 'status'"
        assert first_txn['status'] in ['pending', 'complete'], f"Invalid status: {first_txn['status']}"





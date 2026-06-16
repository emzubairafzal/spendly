from database.queries import (
    get_category_breakdown,
    get_recent_transactions,
    get_summary_stats,
    get_user_by_id,
)


# ── get_user_by_id ────────────────────────────────────────────────────────── #

def test_get_user_by_id_valid(seed_user):
    result = get_user_by_id(seed_user)
    assert result["name"] == "Demo User"
    assert result["email"] == "demo@spendly.com"
    assert result["member_since"] == "January 2026"


def test_get_user_by_id_nonexistent(patched_db):
    assert get_user_by_id(99999) is None


# ── get_summary_stats ─────────────────────────────────────────────────────── #

def test_get_summary_stats_with_expenses(seed_user):
    result = get_summary_stats(seed_user)
    assert result["total_spent"] == "₹296.24"
    assert result["transaction_count"] == 8
    assert result["top_category"] == "Bills"


def test_get_summary_stats_no_expenses(no_expense_user):
    result = get_summary_stats(no_expense_user)
    assert result == {"total_spent": "₹0.00", "transaction_count": 0, "top_category": "—"}


# ── get_recent_transactions ───────────────────────────────────────────────── #

def test_get_recent_transactions_order(seed_user):
    result = get_recent_transactions(seed_user)
    assert len(result) == 8
    assert result[0]["date"] == "16 May 2026"
    for tx in result:
        assert {"date", "description", "category", "amount"} <= tx.keys()
        assert tx["amount"].startswith("₹")


def test_get_recent_transactions_limit(seed_user):
    result = get_recent_transactions(seed_user, limit=3)
    assert len(result) == 3


def test_get_recent_transactions_empty(no_expense_user):
    assert get_recent_transactions(no_expense_user) == []


# ── get_category_breakdown ────────────────────────────────────────────────── #

def test_get_category_breakdown_structure(seed_user):
    result = get_category_breakdown(seed_user)
    assert len(result) == 7
    assert result[0]["name"] == "Bills"
    for cat in result:
        assert cat["amount"].startswith("₹")
        assert {"name", "amount", "pct"} <= cat.keys()


def test_get_category_breakdown_pct_sum(seed_user):
    result = get_category_breakdown(seed_user)
    assert sum(cat["pct"] for cat in result) == 100


def test_get_category_breakdown_pct_ints(seed_user):
    result = get_category_breakdown(seed_user)
    assert all(isinstance(cat["pct"], int) for cat in result)


def test_get_category_breakdown_empty(no_expense_user):
    assert get_category_breakdown(no_expense_user) == []


# ── /profile route ────────────────────────────────────────────────────────── #

def test_profile_unauthenticated(client):
    response = client.get("/profile")
    assert response.status_code == 302
    assert "/login" in response.headers["Location"]


def test_profile_authenticated(logged_in_client):
    response = logged_in_client.get("/profile")
    assert response.status_code == 200


def test_profile_user_info(logged_in_client):
    response = logged_in_client.get("/profile")
    assert b"Demo User" in response.data
    assert b"demo@spendly.com" in response.data


def test_profile_rupee_symbol(logged_in_client):
    response = logged_in_client.get("/profile")
    assert "₹".encode("utf-8") in response.data


def test_profile_total_spent(logged_in_client):
    response = logged_in_client.get("/profile")
    assert b"296.24" in response.data


def test_profile_transaction_count(logged_in_client):
    response = logged_in_client.get("/profile")
    assert b"8" in response.data


def test_profile_top_category(logged_in_client):
    response = logged_in_client.get("/profile")
    assert b"Bills" in response.data


def test_profile_newest_first(logged_in_client):
    response = logged_in_client.get("/profile")
    text = response.data.decode("utf-8")
    assert text.index("16 May") < text.index("1 May 2026")


def test_profile_category_count(logged_in_client):
    response = logged_in_client.get("/profile")
    for category in ("Bills", "Food", "Shopping", "Health", "Other", "Entertainment", "Transport"):
        assert category.encode() in response.data

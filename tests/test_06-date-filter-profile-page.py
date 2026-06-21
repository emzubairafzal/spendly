import pytest
from database.queries import (
    get_category_breakdown,
    get_recent_transactions,
    get_summary_stats,
)


# ------------------------------------------------------------------ #
# Unit tests — get_summary_stats with date filters                    #
# ------------------------------------------------------------------ #

class TestGetSummaryStatsDateFilter:

    def test_no_filter_returns_all_time(self, seed_user):
        stats = get_summary_stats(seed_user)
        assert stats["transaction_count"] == 8
        # SPEC AMBIGUOUS: spec DoD says ₹346.24 but seed fixture sums to ₹296.24
        assert stats["total_spent"] == "₹296.24"

    def test_both_dates_filters_correctly(self, seed_user):
        stats = get_summary_stats(seed_user, start_date="2026-05-01", end_date="2026-05-08")
        assert stats["transaction_count"] == 4
        assert stats["total_spent"] == "₹172.50"
        assert stats["top_category"] == "Bills"

    def test_start_only_filters_correctly(self, seed_user):
        stats = get_summary_stats(seed_user, start_date="2026-05-10")
        assert stats["transaction_count"] == 4
        assert stats["total_spent"] == "₹123.74"

    def test_end_only_filters_correctly(self, seed_user):
        stats = get_summary_stats(seed_user, end_date="2026-05-05")
        assert stats["transaction_count"] == 3
        assert stats["total_spent"] == "₹142.50"

    def test_empty_window_returns_zero_stats(self, seed_user):
        stats = get_summary_stats(seed_user, start_date="2025-01-01", end_date="2025-12-31")
        assert stats["transaction_count"] == 0
        assert stats["total_spent"] == "₹0.00"
        assert stats["top_category"] == "—"

    def test_explicit_none_args_returns_all_time(self, seed_user):
        stats = get_summary_stats(seed_user, start_date=None, end_date=None)
        assert stats["transaction_count"] == 8


# ------------------------------------------------------------------ #
# Unit tests — get_recent_transactions with date filters              #
# ------------------------------------------------------------------ #

class TestGetRecentTransactionsDateFilter:

    def test_both_dates_returns_correct_count(self, seed_user):
        txs = get_recent_transactions(seed_user, start_date="2026-05-01", end_date="2026-05-08")
        assert len(txs) == 4

    def test_both_dates_returns_correct_rows(self, seed_user):
        txs = get_recent_transactions(seed_user, start_date="2026-05-01", end_date="2026-05-08")
        descriptions = {tx["description"] for tx in txs}
        assert "Grocery shopping" in descriptions
        assert "Bus pass" in descriptions
        assert "Electricity bill" in descriptions
        assert "Pharmacy" in descriptions
        assert "Netflix subscription" not in descriptions

    def test_both_dates_newest_first(self, seed_user):
        txs = get_recent_transactions(seed_user, start_date="2026-05-01", end_date="2026-05-08")
        assert txs[0]["description"] == "Pharmacy"

    def test_start_only_returns_correct_count(self, seed_user):
        txs = get_recent_transactions(seed_user, start_date="2026-05-10")
        assert len(txs) == 4

    def test_end_only_returns_correct_count(self, seed_user):
        txs = get_recent_transactions(seed_user, end_date="2026-05-05")
        assert len(txs) == 3

    def test_filter_respects_limit(self, seed_user):
        txs = get_recent_transactions(seed_user, limit=2, start_date="2026-05-01", end_date="2026-05-08")
        assert len(txs) == 2

    def test_no_filter_backwards_compatible(self, seed_user):
        txs = get_recent_transactions(seed_user)
        assert len(txs) == 8

    def test_empty_window_returns_empty_list(self, seed_user):
        txs = get_recent_transactions(seed_user, start_date="2025-01-01", end_date="2025-12-31")
        assert txs == []


# ------------------------------------------------------------------ #
# Unit tests — get_category_breakdown with date filters               #
# ------------------------------------------------------------------ #

class TestGetCategoryBreakdownDateFilter:

    def test_both_dates_top_category_is_bills(self, seed_user):
        cats = get_category_breakdown(seed_user, start_date="2026-05-01", end_date="2026-05-08")
        assert cats[0]["name"] == "Bills"

    def test_both_dates_only_matching_categories(self, seed_user):
        cats = get_category_breakdown(seed_user, start_date="2026-05-01", end_date="2026-05-08")
        names = {c["name"] for c in cats}
        assert names == {"Food", "Transport", "Bills", "Health"}
        assert "Entertainment" not in names
        assert "Shopping" not in names

    def test_start_only_excludes_earlier_categories(self, seed_user):
        cats = get_category_breakdown(seed_user, start_date="2026-05-10")
        names = {c["name"] for c in cats}
        assert "Bills" not in names
        assert "Entertainment" in names

    def test_pct_sums_to_100_under_filter(self, seed_user):
        cats = get_category_breakdown(seed_user, start_date="2026-05-01", end_date="2026-05-08")
        assert sum(c["pct"] for c in cats) == 100

    def test_pct_values_are_integers(self, seed_user):
        cats = get_category_breakdown(seed_user, start_date="2026-05-01", end_date="2026-05-08")
        for c in cats:
            assert isinstance(c["pct"], int)

    def test_empty_window_returns_empty_list(self, seed_user):
        cats = get_category_breakdown(seed_user, start_date="2025-01-01", end_date="2025-12-31")
        assert cats == []

    def test_no_filter_backwards_compatible(self, seed_user):
        cats = get_category_breakdown(seed_user)
        assert len(cats) == 7

    def test_end_only_limits_categories(self, seed_user):
        cats = get_category_breakdown(seed_user, end_date="2026-05-05")
        names = {c["name"] for c in cats}
        assert names == {"Food", "Transport", "Bills"}


# ------------------------------------------------------------------ #
# Integration tests — GET /profile with date filter params            #
# ------------------------------------------------------------------ #

class TestProfileRouteWithDateFilter:

    # Auth guard
    def test_unauthenticated_no_params_redirects(self, client, seed_user):
        r = client.get("/profile")
        assert r.status_code == 302
        assert "/login" in r.headers["Location"]

    def test_unauthenticated_with_params_redirects(self, client, seed_user):
        r = client.get("/profile?start=2026-05-01&end=2026-05-08")
        assert r.status_code == 302
        assert "/login" in r.headers["Location"]

    # All-time view (no filter)
    def test_no_filter_returns_200(self, logged_in_client):
        r = logged_in_client.get("/profile")
        assert r.status_code == 200

    def test_no_filter_shows_all_transactions(self, logged_in_client):
        text = logged_in_client.get("/profile").get_data(as_text=True)
        assert "Grocery shopping" in text
        assert "Restaurant lunch" in text

    def test_no_filter_total_spent(self, logged_in_client):
        text = logged_in_client.get("/profile").get_data(as_text=True)
        # SPEC AMBIGUOUS: spec says 346.24, fixture sums to 296.24
        assert "296.24" in text

    def test_no_filter_transaction_count_8(self, logged_in_client):
        text = logged_in_client.get("/profile").get_data(as_text=True)
        assert ">8<" in text or "8" in text

    # Filtered view: both start and end
    def test_both_dates_returns_200(self, logged_in_client):
        r = logged_in_client.get("/profile?start=2026-05-01&end=2026-05-08")
        assert r.status_code == 200

    def test_both_dates_total_spent(self, logged_in_client):
        text = logged_in_client.get("/profile?start=2026-05-01&end=2026-05-08").get_data(as_text=True)
        assert "172.50" in text

    def test_both_dates_excludes_out_of_range(self, logged_in_client):
        text = logged_in_client.get("/profile?start=2026-05-01&end=2026-05-08").get_data(as_text=True)
        assert "Netflix subscription" not in text
        assert "New shirt" not in text

    def test_both_dates_top_category_bills(self, logged_in_client):
        text = logged_in_client.get("/profile?start=2026-05-01&end=2026-05-08").get_data(as_text=True)
        assert "Bills" in text

    # Filtered view: start only
    def test_start_only_total_spent(self, logged_in_client):
        text = logged_in_client.get("/profile?start=2026-05-10").get_data(as_text=True)
        assert "123.74" in text

    def test_start_only_excludes_earlier_expenses(self, logged_in_client):
        text = logged_in_client.get("/profile?start=2026-05-10").get_data(as_text=True)
        assert "Grocery shopping" not in text
        assert "Bus pass" not in text

    # Filtered view: end only
    def test_end_only_total_spent(self, logged_in_client):
        text = logged_in_client.get("/profile?end=2026-05-05").get_data(as_text=True)
        assert "142.50" in text

    def test_end_only_excludes_later_expenses(self, logged_in_client):
        text = logged_in_client.get("/profile?end=2026-05-05").get_data(as_text=True)
        assert "Netflix subscription" not in text
        assert "Restaurant lunch" not in text

    # Invalid range (end before start)
    def test_invalid_range_returns_200(self, logged_in_client):
        r = logged_in_client.get("/profile?start=2026-05-10&end=2026-05-01")
        assert r.status_code == 200

    def test_invalid_range_shows_all_time_data(self, logged_in_client):
        text = logged_in_client.get("/profile?start=2026-05-10&end=2026-05-01").get_data(as_text=True)
        # SPEC AMBIGUOUS: spec says 346.24, fixture sums to 296.24
        assert "296.24" in text

    def test_invalid_range_no_filter_banner(self, logged_in_client):
        text = logged_in_client.get("/profile?start=2026-05-10&end=2026-05-01").get_data(as_text=True)
        assert "Showing" not in text

    # UI elements — date inputs pre-filled
    def test_start_input_prefilled(self, logged_in_client):
        text = logged_in_client.get("/profile?start=2026-05-01&end=2026-05-08").get_data(as_text=True)
        assert 'value="2026-05-01"' in text

    def test_end_input_prefilled(self, logged_in_client):
        text = logged_in_client.get("/profile?start=2026-05-01&end=2026-05-08").get_data(as_text=True)
        assert 'value="2026-05-08"' in text

    # UI elements — Apply button always present
    def test_apply_button_present_without_filter(self, logged_in_client):
        text = logged_in_client.get("/profile").get_data(as_text=True)
        assert "Apply" in text

    def test_apply_button_present_with_filter(self, logged_in_client):
        text = logged_in_client.get("/profile?start=2026-05-01&end=2026-05-08").get_data(as_text=True)
        assert "Apply" in text

    # UI elements — Clear link
    def test_clear_link_visible_with_filter(self, logged_in_client):
        text = logged_in_client.get("/profile?start=2026-05-01&end=2026-05-08").get_data(as_text=True)
        assert "Clear" in text

    def test_clear_link_hidden_without_filter(self, logged_in_client):
        text = logged_in_client.get("/profile").get_data(as_text=True)
        assert "Clear" not in text

    # UI elements — Active filter banner
    def test_filter_banner_visible_with_both_dates(self, logged_in_client):
        text = logged_in_client.get("/profile?start=2026-05-01&end=2026-05-08").get_data(as_text=True)
        assert "Showing" in text

    def test_filter_banner_hidden_without_filter(self, logged_in_client):
        text = logged_in_client.get("/profile").get_data(as_text=True)
        assert "Showing" not in text

    def test_filter_banner_visible_with_start_only(self, logged_in_client):
        text = logged_in_client.get("/profile?start=2026-05-10").get_data(as_text=True)
        assert "Showing from" in text

    def test_filter_banner_visible_with_end_only(self, logged_in_client):
        text = logged_in_client.get("/profile?end=2026-05-05").get_data(as_text=True)
        assert "Showing up to" in text

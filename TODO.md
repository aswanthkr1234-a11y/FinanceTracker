# TODO - FinanceTracker

## Completed Fixes

- [x] **Fixed `database.py`** — Added migration checks for missing `username` and `date` columns on both `income` and `expense` tables.
- [x] **Fixed `app.py` syntax errors**:
  - Line 67: `WHERE username=?,` → `WHERE username=?` (removed stray comma)
  - Lines 88-103: Missing comma before params tuple `""" (username,))` → `""", (username,))`
  - Lines 105-109: Recent income query missing `WHERE username=?` filter
- [x] **Fixed `app.py` SUM queries** — Added `WHERE username=?` filter to `SELECT SUM(amount)` queries so totals are per-user, not global.
- [x] **Fixed `add_income` INSERT** — Now includes `category` and `date` fields matching the form.
- [x] **Ran database migration** — Added `username` and `date` columns to existing `income` and `expense` tables.

## Remaining
- [ ] Update dashboard bar chart controls to make the amount option above the chart more useful.
- [ ] Adjust HTML in templates/index.html to replace/remove the simplistic amount control with improved UI.
- [ ] Adjust JS in templates/index.html (or static/js) to support the new control.
- [ ] Run quick sanity check by starting the Flask app and verifying chart behavior.


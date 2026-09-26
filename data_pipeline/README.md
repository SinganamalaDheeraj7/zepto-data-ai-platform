# Data pipeline

Run `python pipeline.py`. It scrapes the first three catalogue categories (well over 60 books), cleans fields, recreates `catalogue.db`, and writes `clean_books.csv` and `query_results.md`.

`price_gbp` is parsed as a float; textual ratings map One–Five to integers; availability becomes a Boolean. Malformed numeric prices use median imputation, while rows missing essential identity/category/rating data are dropped because these cannot be defensibly inferred. INR is calculated at the required fixed baseline: **1 GBP = 105.50 INR**. The SQLite design has `categories` (PK) and `books` (PK with `category_id` FK). The generated query log covers WHERE, ORDER BY, LIMIT, DISTINCT, BETWEEN, and a JOIN; it also includes a pandas merge equivalent of the JOIN.

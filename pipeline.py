"""Scrape, clean, normalize, query, and compare the Books to Scrape catalogue."""
from __future__ import annotations
import re, sqlite3
from urllib.parse import urljoin
from pathlib import Path
import pandas as pd
import requests
from bs4 import BeautifulSoup

ROOT = Path(__file__).parent
DB = ROOT / "catalogue.db"
RATE = 105.50
RATINGS = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}

def soup(url: str) -> BeautifulSoup:
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    return BeautifulSoup(response.text, "html.parser")

def scrape() -> pd.DataFrame:
    home = soup("https://books.toscrape.com/")
    category_links = home.select("ul.nav-list ul li a")[:3]
    rows = []
    for link in category_links:
        category, url = link.get_text(strip=True), urljoin("https://books.toscrape.com/", link["href"])
        while url:
            page = soup(url)
            for book in page.select("article.product_pod"):
                rows.append({"title": book.h3.a["title"], "price": book.select_one(".price_color").get_text(strip=True),
                             "star_rating": book.p["class"][1], "availability": book.select_one(".availability").get_text(" ", strip=True), "category": category})
            nxt = page.select_one("li.next a")
            url = urljoin(url, nxt["href"]) if nxt else None
    return pd.DataFrame(rows)

def clean(raw: pd.DataFrame) -> pd.DataFrame:
    df = raw.copy()
    df["price_gbp"] = pd.to_numeric(df.price.str.replace(r"[^0-9.]", "", regex=True), errors="coerce")
    df["rating"] = df.star_rating.map(RATINGS)
    df["in_stock"] = df.availability.str.contains("In stock", case=False, na=False)
    # Numeric malformed values receive median imputation; rows missing category/title/rating are dropped.
    df["price_gbp"] = df["price_gbp"].fillna(df["price_gbp"].median())
    df = df.dropna(subset=["title", "category", "rating"]).copy()
    df["rating"] = df.rating.astype(int); df["in_stock"] = df.in_stock.astype(bool)
    df["price_inr"] = (df.price_gbp * RATE).round(2)
    return df[["title", "price_gbp", "price_inr", "rating", "in_stock", "category"]]

def load(df: pd.DataFrame) -> None:
    with sqlite3.connect(DB) as con:
        con.executescript("""PRAGMA foreign_keys=ON; DROP TABLE IF EXISTS books; DROP TABLE IF EXISTS categories;
        CREATE TABLE categories(category_id INTEGER PRIMARY KEY, category_name TEXT UNIQUE NOT NULL);
        CREATE TABLE books(book_id INTEGER PRIMARY KEY, title TEXT NOT NULL, price_gbp REAL NOT NULL, price_inr REAL NOT NULL,
          rating INTEGER NOT NULL CHECK(rating BETWEEN 1 AND 5), in_stock INTEGER NOT NULL, category_id INTEGER NOT NULL,
          FOREIGN KEY(category_id) REFERENCES categories(category_id));""")
        pd.DataFrame({"category_name": sorted(df.category.unique())}).to_sql("categories", con, if_exists="append", index=False)
        ids = pd.read_sql("SELECT * FROM categories", con)
        df.merge(ids, left_on="category", right_on="category_name").drop(columns=["category", "category_name"]).assign(in_stock=lambda x: x.in_stock.astype(int)).to_sql("books", con, if_exists="append", index=False)

QUERIES = {
 "where": "SELECT title, price_gbp FROM books WHERE in_stock=1 LIMIT 5",
 "order_limit": "SELECT title, price_inr FROM books ORDER BY price_inr DESC LIMIT 10",
 "distinct": "SELECT DISTINCT rating FROM books ORDER BY rating",
 "between": "SELECT title, rating FROM books WHERE rating BETWEEN 4 AND 5 LIMIT 10",
 "join": "SELECT c.category_name, b.title, b.rating, b.price_gbp FROM books b JOIN categories c ON b.category_id=c.category_id ORDER BY b.rating DESC, b.price_gbp DESC LIMIT 10",
}
def demonstrate() -> None:
    with sqlite3.connect(DB) as con:
        output=[]
        for name, sql in QUERIES.items():
            result=pd.read_sql(sql, con); output += [f"## {name}\n```sql\n{sql}\n```\n{result.to_markdown(index=False)}\n"]
        books=pd.read_sql("SELECT * FROM books", con); cats=pd.read_sql("SELECT * FROM categories", con)
        merged=books.merge(cats, on="category_id").sort_values(["rating","price_gbp"], ascending=[False,False]).head(10)
        output += ["## pandas merge equivalent to join\n" + merged[["category_name","title","rating","price_gbp"]].to_markdown(index=False)]
        (ROOT/"query_results.md").write_text("\n".join(output), encoding="utf-8")
if __name__ == "__main__":
    cleaned=clean(scrape()); assert len(cleaned)>=60 and cleaned.category.nunique()>=3
    load(cleaned); cleaned.to_csv(ROOT/"clean_books.csv", index=False); demonstrate(); print(f"Loaded {len(cleaned)} books into {DB}")

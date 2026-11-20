"""
Search your speaker archive. Every hit comes with the file and slide/page number.

    python tools/search.py "D:/Talks" "first three seconds"
    python tools/search.py "D:/Talks" "нейросети AND бизнес" --limit 30

The query uses SQLite FTS5 syntax: words, "exact phrases", AND / OR / NOT, prefix*.
"""
import argparse, sqlite3, sys
from pathlib import Path


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("folder")
    ap.add_argument("query")
    ap.add_argument("--limit", type=int, default=20)
    a = ap.parse_args()
    db = sqlite3.connect(Path(a.folder).resolve() / "_ai" / "kb.sqlite3")
    q = a.query
    if not any(op in q for op in ('"', " AND ", " OR ", " NOT ", "*")) and " " in q:
        q = f'"{q}"'  # treat plain multi-word input as a phrase
    try:
        rows = db.execute("""SELECT path, kind, number, snippet(search, 3, '[', ']', ' … ', 14)
                             FROM search WHERE search MATCH ? ORDER BY rank LIMIT ?""", (q, a.limit)).fetchall()
    except sqlite3.OperationalError as e:
        sys.exit(f"Query error: {e}")
    if not rows:
        print("No results. Try fewer words, synonyms, the other language, or prefix* search.")
    for path, kind, num, snip in rows:
        where = {"slide": f"slide {num}", "page": f"page {num}"}.get(kind, f"{kind} {num}" if num not in (0, "0") else kind)
        print(f"{path}  ·  {where}\n    {' '.join(snip.split())}\n")


if __name__ == "__main__":
    main()

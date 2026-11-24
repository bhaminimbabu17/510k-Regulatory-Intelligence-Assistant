"""Command-line app: python -m src.app "infusion pump" [options]"""
import argparse
import sys

from src.fda_client import FDAClient, FDADataUnavailable
from src.landscape import build_landscape, format_landscape, load_summary_texts
from src.results import filter_results, format_result, format_table
from src.search import search_devices

DISCLAIMER = ("Research support only. This tool does not make regulatory pathway "
              "determinations; review the FDA source records yourself.")


def build_parser():
    p = argparse.ArgumentParser(description="510(k) Regulatory Intelligence Assistant")
    p.add_argument("query", help="device name, description or 3-letter product code")
    p.add_argument("--limit", type=int, default=20, help="maximum results (default 20)")
    p.add_argument("--product-code", help="only show this product code")
    p.add_argument("--from-year", type=int, help="earliest decision year")
    p.add_argument("--to-year", type=int, help="latest decision year")
    p.add_argument("--landscape", action="store_true",
                   help="show the regulatory landscape (applicants, codes, years, predicates)")
    p.add_argument("--summaries-dir",
                   help="folder of 510(k) summary text files named <K number>.txt, "
                        "used to extract predicates")
    return p


def main(argv=None, client=None):
    args = build_parser().parse_args(argv)
    client = client or FDAClient()
    try:
        found = search_devices(args.query, client, limit=args.limit)
    except FDADataUnavailable as error:  # FR-2.3
        print(f"Error: {error}. Please try again later.")
        return 1
    except ValueError as error:
        print(f"Error: {error}")
        return 2

    results = filter_results([format_result(r) for r in found.records],
                             args.product_code, args.from_year, args.to_year)
    print(f"{len(results)} submission(s) for \"{args.query}\"\n")
    print(format_table(results))
    if found.suggestions:  # FR-1.2 / FR-1.3
        print("\nFew results. Suggestions:")
        for s in found.suggestions:
            print(f"  - {s}")
    if args.landscape:
        texts = load_summary_texts(args.summaries_dir, [r["k_number"] for r in results])
        print("\n" + format_landscape(build_landscape(results, texts)))
    print(f"\n{DISCLAIMER}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
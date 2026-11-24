"""Command-line app: python -m src.app "infusion pump" [options]"""
import argparse
import sys

from src.fda_client import FDAClient, FDADataUnavailable
from src.landscape import format_landscape, summarize_landscape
from src.predicates import get_predicates
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
    p.add_argument("--landscape", action="store_true", help="show patterns across results")
    p.add_argument("--predicates", action="store_true",
                   help="read summary PDFs for predicate devices (slower)")
    return p


def main(argv=None, client=None, pdf_session=None):
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
    if args.landscape or args.predicates:
        info = None
        if args.predicates:
            info = [get_predicates(r["k_number"], pdf_session) for r in results]
        print("\n" + format_landscape(summarize_landscape(results, info)))
    if found.suggestions:  # FR-1.2 / FR-1.3
        print("\nFew results. Suggestions:")
        for s in found.suggestions:
            print(f"  - {s}")
    print(f"\n{DISCLAIMER}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
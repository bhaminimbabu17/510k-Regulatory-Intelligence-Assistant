"""Command-line app: python -m src.app "infusion pump" [options]"""
import argparse
import sys

from src.ai_client import call_model
from src.ai_summary import summarize_submission
from src.fda_client import FDAClient, FDADataUnavailable
from src.insights import build_insights, format_insights
from src.landscape import format_landscape, summarize_landscape
from src.predicates import fetch_summary_text, get_predicates
from src.results import filter_results, format_result, format_table
from src.search import search_devices
from src.traceability import format_ai_output, release

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
    p.add_argument("--summarize", type=int, metavar="N", default=0,
                   help="AI summaries for the first N results (needs ANTHROPIC_API_KEY)")
    p.add_argument("--insights", action="store_true",
                   help="patterns across results, with an AI narrative if a key is set")
    return p


def main(argv=None, client=None, pdf_session=None, model=call_model):
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
    retrieved = [r["k_number"] for r in results]
    if args.landscape or args.predicates or args.insights:
        info = None
        if args.predicates:
            info = [get_predicates(r["k_number"], pdf_session) for r in results]
        summary = summarize_landscape(results, info)
        if args.landscape or args.predicates:
            print("\n" + format_landscape(summary))
        if args.insights:
            print("\n" + format_insights(build_insights(summary, retrieved, model)))
    for r in results[:args.summarize]:
        text = fetch_summary_text(r["k_number"], pdf_session)
        item = release(summarize_submission(r, text, model), retrieved)  # FR-7.2
        print("\n" + r["k_number"] + "\n" + format_ai_output(item))
    if found.suggestions:  # FR-1.2 / FR-1.3
        print("\nFew results. Suggestions:")
        for s in found.suggestions:
            print(f"  - {s}")
    print(f"\n{DISCLAIMER}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
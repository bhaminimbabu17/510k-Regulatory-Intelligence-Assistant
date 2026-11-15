# 510(k) Regulatory Intelligence Assistant

CISC 594 semester project. A tool that lets a user enter a medical device name
or description, finds relevant FDA 510(k) submissions through the openFDA API,
organizes them into a regulatory landscape view, and (in Version 2) adds
AI-generated summaries linked to the FDA source records.

The system supports research only and does not make regulatory pathway
determinations.

See `CM_PLAN.md` for how changes, baselines and releases are controlled.

## Run the tests

    pip install -r requirements.txt
    python -m pytest

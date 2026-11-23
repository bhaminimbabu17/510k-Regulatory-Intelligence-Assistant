# Software Requirements

Derived from the Q1/Q2/Q3 analysis in the Risk-Driven Development and
Verification workbook. Format: "<module> shall <behavior> within <constraint>".
Q1 = desired behavior, Q2 = preventative behavior, Q3 = responsive behavior.

## R-01 Relevant submissions missed (Search)

| ID | Type | Requirement | Rationale |
|---|---|---|---|
| FR-1.1 | Q1 | Search Service shall return submissions whose device name, synonym or product code matches the user's query within one search request. | Users describe devices differently from FDA naming; matching synonyms and product codes finds more relevant submissions. |
| FR-1.2 | Q2 | Search Service shall not return an empty result without suggesting alternative search terms. | An empty page with no guidance hides the fact that relevant submissions may exist. |
| FR-1.3 | Q3 | Search Service shall suggest broader terms and a product-code search when fewer than 3 results are found. | Gives the user a next step when the search was too narrow. |

## R-02 FDA data unavailable (FDA Client)

| ID | Type | Requirement | Rationale |
|---|---|---|---|
| FR-2.1 | Q1 | FDA Client shall retrieve 510(k) records from the openFDA API within 10 seconds per request. | Users need results quickly; a timeout stops the app from hanging. |
| FR-2.2 | Q2 | FDA Client shall cache identical requests and send an API key when one is configured, so the daily request limit is not exceeded. | Without a key openFDA allows 1,000 requests a day; caching and a key keep the app under the limit. |
| FR-2.3 | Q3 | FDA Client shall raise an "FDA data unavailable" error, which the app shall display, when openFDA fails or times out. | Users are told clearly that data is missing instead of seeing an empty or misleading result. |

## R-03 Incomplete record shown as complete (Results)

| ID | Type | Requirement | Rationale |
|---|---|---|---|
| FR-3.1 | Q1 | Results Module shall display, for each submission, the 510(k) number, device name, applicant, decision date, product code and a link to the FDA record. | These are the fields users compare when reviewing the landscape. |
| FR-3.2 | Q2 | Results Module shall not display a missing field as blank. | A blank looks like "nothing to report" rather than "data missing". |
| FR-3.3 | Q3 | Results Module shall label each missing field "Not available". | Users can see exactly which data is missing and check the FDA source. |

## R-04 Predicate relationships missing (Landscape)

| ID | Type | Requirement | Rationale |
|---|---|---|---|
| FR-4.1 | Q1 | Predicate Extractor shall extract predicate 510(k) numbers from a submission's summary text. | Predicates are not in the openFDA API; they appear in the 510(k) summary. |
| FR-4.2 | Q2 | Landscape Module shall not present a predicate list as complete when extraction failed for any submission. | Prevents users from assuming no predicates exist. |
| FR-4.3 | Q3 | Landscape Module shall mark predicates "Not extracted" and give the summary PDF link when extraction fails. | Users can check the source document themselves. |

## R-05 Hallucinated AI summary (AI Summary)

| ID | Type | Requirement | Rationale |
|---|---|---|---|
| FR-5.1 | Q1 | Summary Service shall generate each summary only from the selected submission's openFDA record and 510(k) summary text. | Limits the model to source material, lowering the chance of invented content. |
| FR-5.2 | Q2 | Summary Validator shall block any summary statement that cannot be matched to the source before it is displayed. | Stops unsupported claims from reaching the user. |
| FR-5.3 | Q3 | Summary Service shall label a summary with blocked statements "Unverified", log it, and display the source link in the same output. | Users still reach accurate information when the AI fails. |

## R-06 AI insight reads as regulatory advice (Insights)

| ID | Type | Requirement | Rationale |
|---|---|---|---|
| FR-6.1 | Q1 | Insights Module shall describe recurring applicants, product codes and predicates across the retrieved submissions. | Gives users patterns to investigate further. |
| FR-6.2 | Q2 | Insights Module shall block any insight containing pathway-determination language such as "qualifies for", "should use the" or "is substantially equivalent". | The system must not present regulatory determinations. |
| FR-6.3 | Q3 | Insights Module shall attach the research-only disclaimer to every insight. | Reminds users that a qualified person must make regulatory decisions. |

## R-07 AI output not linked to sources (Traceability)

| ID | Type | Requirement | Rationale |
|---|---|---|---|
| FR-7.1 | Q1 | Traceability Module shall attach the source 510(k) numbers and FDA links to every AI output. | Users can verify every AI statement. |
| FR-7.2 | Q2 | Traceability Module shall not release AI output that has no source among the retrieved submissions. | Unverifiable output is not shown as if it were verified. |
| FR-7.3 | Q3 | Traceability Module shall withhold such output and display "Source could not be verified". | Users know output was withheld and why. |

## R-09 Scope creep (process)

Mitigated by the change control process in `CM_PLAN.md`, not by software;
no software requirements.
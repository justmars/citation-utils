# Summary

## Concept

The `Report` Model from [citation-report](https://github.com/justmars/citation-report) is only one part of a Philippine Supreme Court citation. This library will handle the patterns involved with respect to the `Docket`.

Let's look at sample citation that is typically found in the body and the footnotes section of a decision:

> Bagong Alyansang Makabayan v. Zamora, G.R. Nos. 138570, 138572, 138587, 138680, 138698, October 10, 2000, 342 SCRA 449

We can separate the `Docket` portion from the `Report` portion:

Docket | Report
--:|:--
G.R. Nos. 138570, 138572, 138587, 138680, 138698, October 10, 2000 | 342 SCRA 449

## Utility

Both [citation-reports](https://github.com/justmars/citation-report) and [citation-docket](https://github.com/justmars/citation-docket) are dependencies of [citation-utils](https://github.com/justmars/citation-utils).

Like [citation-reports](https://github.com/justmars/citation-report), there is a problem involving inconsistent use of values. We address it the same way by dissecting the component parts and generating a uniform citation.

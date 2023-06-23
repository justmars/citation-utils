# API

## CitableDocument

A `Citation`'s `extract_citations()` function relies on a `CitableDocument`.

:::citation_utils.CitableDocument

## Docket Model

:::citation_utils.dockets.Docket

## Docket Category

### Docket Category Model

:::citation_utils.dockets.DocketCategory

## Docket CitationConstructor

Although the different category docket models share a similar configuration, the regex strings involved are different for each, prompting the need for a preparatory constructor class:

:::citation_utils.dockets.models.CitationConstructor

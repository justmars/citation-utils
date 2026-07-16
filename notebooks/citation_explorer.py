import marimo

__generated_with = "0.23.14"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import polars as pl

    from citation_utils import Citation, CountedCitation

    return Citation, CountedCitation, mo, pl


@app.cell
def _(mo):
    source = mo.ui.text_area(
        label="Citation text",
        value=(
            "G.R. No. 147033, April 30, 2003, 374 Phil. 1; "
            "G.R. No. 147033, April 30, 2003; 31 SCRA 562"
        ),
        full_width=True,
    )
    return (source,)


@app.cell
def _(Citation, CountedCitation, pl, source):
    citation_schema = {
        "cat": pl.String,
        "num": pl.String,
        "date": pl.String,
        "phil": pl.String,
        "scra": pl.String,
        "offg": pl.String,
    }
    mention_schema = citation_schema | {"mentions": pl.Int64}

    citation_rows = [
        citation.model_dump() for citation in Citation.extract_citations(source.value)
    ]
    mention_rows = [
        citation.model_dump() for citation in CountedCitation.from_source(source.value)
    ]
    citations = pl.DataFrame(citation_rows, schema=citation_schema)
    mentions = pl.DataFrame(mention_rows, schema=mention_schema)
    return citations, mentions


@app.cell
def _(citations, mentions, mo, source):
    mo.vstack(
        [
            mo.md("# Citation explorer"),
            source,
            mo.md("## Extracted citations"),
            mo.ui.table(citations),
            mo.md("## Citation mentions"),
            mo.ui.table(mentions),
        ]
    )
    return


if __name__ == "__main__":
    app.run()

"""RBI Handbook of States: fiscal tables by state, checked against the all-states total."""
from pipelines.sources.rbi.state_finances import SOURCE


def parse(raw_from, *names):
    raws = []
    for n in names:
        raw = raw_from(f"rbi/handbook/{n}T_x.XLSX")
        raws.append(raw.__class__(content=raw.content, url=f"https://rbidocs.rbi.org.in/x/{n}T_x.XLSX",
                                  fetched_at=raw.fetched_at, sha256=raw.sha256, suffix=raw.suffix))
    return SOURCE.parse(raws)


def at(df, sid, state, period):
    return df[(df.series_id == sid) & (df.entity == state) & (df.period == period)].value.item()


def test_gfd_and_stage(raw_from):
    df = parse(raw_from, 164)
    assert at(df, "state_gfd", "Andhra Pradesh", "2022-04-01") == 0.52508           # Rs 52,508 crore
    note = df[(df.series_id == "state_gfd") & (df.period == "2023-04-01")].note.unique().tolist()
    assert note == ["Revised Estimates"]
    assert "Delhi" in set(df.entity)                                                 # "NCT Delhi" alias


def test_misaligned_year_dropped(raw_from, capsys):
    df = parse(raw_from, 176)
    liab = df[df.series_id == "state_liabilities"]
    assert "2014-04-01" not in set(liab.period)                                      # end-March 2015 sheet
    assert "rows misaligned" in capsys.readouterr().out
    assert "2023-04-01" in set(liab.period)


def test_gsdp_units(raw_from):
    df = parse(raw_from, 21)
    assert at(df, "state_gsdp_current", "Andhra Pradesh", "2024-04-01") == 15.93062   # Rs lakh -> lakh crore

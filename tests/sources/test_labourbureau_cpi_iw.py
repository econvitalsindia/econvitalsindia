

def test_press_link_both_names():
    from pipelines.sources.labourbureau.cpi_iw import press_link
    base = "https://labourbureau.gov.in/uploads/public/notice/"
    old = f'<a href="{base}Press-Release-CPI-IW-August-2026pdf-1a.pdf">'
    new = f'<a href="{base}MIL-CPI-IW-Sept-2026Epdf-d4.pdf"><a href="{base}Press-ReleaseCPIIWSept-2026Epdf-da.pdf">'
    assert press_link(old).endswith("Press-Release-CPI-IW-August-2026pdf-1a.pdf")
    assert press_link(new).endswith("Press-ReleaseCPIIWSept-2026Epdf-da.pdf")     # not the MIL leaflet

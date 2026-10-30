# 0005: No analysis of individual MPC members or speech tone

- **Date:** 2026-10-30
- **Decision:** the maintainer dropped MPC Speak (hawk–dove scoring of each member's statement
  in the minutes, the committee tone average, and per-member dissent records). Do not rebuild
  it, or any other per-member or speech/tone analysis (speeches, statements, sentiment scores).
- **Kept:** the MPC decisions table on the Money page (rate, change, stance, RBI's projections)
  and the committee's vote tally on the rate resolution ("5–1"), counted from the minutes
  without storing names (pipelines/sources/rbi/_minutes.py, `vote_count`).
- **Where the old code is:** archive/mpc-speak/ (not built, fetched or tested; the maintainer
  deletes it).

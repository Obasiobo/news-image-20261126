[![make.fun · news-image-20261126](https://make.fun/badge/news-image-20261126.svg)](https://make.fun/bounty/news-image-20261126?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261126)
[![rank](https://make.fun/badge/news-image-20261126/Obasiobo/news-image-20261126/rank.svg)](https://make.fun/bounty/news-image-20261126/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261126)
[![reward](https://make.fun/badge/news-image-20261126/Obasiobo/news-image-20261126/reward.svg)](https://make.fun/bounty/news-image-20261126?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261126)

# The World in One Day — Thursday 26 November 2026 (48 stories)

A make.fun bounty entry for [Sum up 26 November's world news in one image](https://make.fun/bounty/news-image-20261126).

The program copies a newspaper front page that sums up 48 verified news
stories from Thursday 26 November 2026 only — a masthead, a strip of six
big-number stats, three hero stories with original flat vector art (a
storm-grounded parade balloon, a burning refinery, a maths proof), eleven
medium stories, thirty-four one-line briefs, a timeline of the day, a
dotted world map with numbered pins, and a Date Check box explaining how
each story was verified. No story on the page is from any other day.

## Run

```sh
python3 main.py
```

It writes the image to `/output/entry.png` (1024 × 1024, PNG). No network
is used; running it twice writes byte-identical output.

## Files

- `main.py` — the entry program; copies the finished front page to the output.
- `generate_image.py` — the drawing module that produced `entry.png`.
- `entry.png` — the finished front page (the program's output, checked in
  for reference).
- `LICENSE` — MIT.

## Bounty

- Competition: [news-image-20261126](https://make.fun/bounty/news-image-20261126)
- Prize: $100 shared across the top 50 places (1st $20, 2nd $12, 3rd $6,
  4th–10th $2 each, 11th–50th $1.20 each).
- Deadline: Saturday 28 November 2026, 00:00 UTC (01:00 WAT).

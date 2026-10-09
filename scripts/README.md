# Profile artwork generators

The generators draw the artwork in code using SVG, resvg, and Pillow. They use
the pinned dependencies in `bunny-requirements.txt`.

## Install dependencies

From the repository root, run:

```sh
python -m pip install -r scripts/bunny-requirements.txt
```

## Pink curiosity and technology banner

```sh
python scripts/build_profile_banner.py
```

This rebuilds `assets/pink-banner.gif` and `assets/profile-banner.svg`.
The GIF contains 120 frames, loops continuously, and has transparent corners.
It includes a laptop bunny, a phone bunny, a walking bunny, and the animated
learning message. Its tagline explores technology broadly. The renderer verifies the frame count, looping, and transparency.

To inspect several decoded animation frames without adding them to the profile:

```sh
python scripts/build_profile_banner.py --output-dir preview/banner --preview-dir preview/frames
```

Only commit the two final assets when changing the banner. The frame PNGs are
local review files and are not used by the README. Edit the `banner` and `bunny`
functions to change the wording, colors, or animation.

## Contribution garden

The existing `build_bunny_calendar.py` fetches real contribution dates and counts
from GitHub and generates the rolling calendar and yearly bunny calendars.
The scheduled **Pink bunny contribution garden** workflow checks for updates every five minutes and after pushes to `main`.
To refresh it manually, open that workflow in Actions and choose **Run workflow**.
Unchanged calendars reuse their existing animations, so frequent checks do not create empty asset updates. A timestamp shows when each calendar was last rendered, and versioned image URLs refresh cached images after the data changes. GitHub scheduling and contribution processing can introduce delays; the README is a periodically updated snapshot.
The banner generator does not need a GitHub token and does not read repository data.

## Pink profile cards

```sh
python scripts/build_profile_cards.py
```

This redraws the six curiosity cards, the learn/build/share/grow path, and the two
contact buttons. These are interest and goal illustrations, not proficiency claims.
The final SVGs are `curiosity-corner.svg`, `little-steps.svg`, `contact-linkedin.svg`,
and `contact-email.svg` in `assets/`.

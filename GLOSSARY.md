# Europa-Park Crowd Forecast

Predicts how crowded Europa-Park will be on each open day of a season, so a visitor can pick a quiet day.

## Calendar

**Season**:
One uninterrupted run of open days, either a summer season or a winter season. Summer and winter are always separate seasons.
_Avoid_: Year, period

**Summer season**:
The main season, from opening day in spring to the last day of Halloween in early November.

**Winter season**:
The shorter season from late November to early January.
_Avoid_: Christmas season

**Halloween phase**:
The final part of the summer season, when the park runs its Halloween theme.

**Bridge day**:
A working day between a public holiday and a weekend, often taken off.
_Avoid_: Brückentag, Fenstertag

**Open day**:
A calendar day on which the park is open to visitors. Only open days get a crowd level.
_Avoid_: Operating day, park day

## Crowd

**Crowd level**:
One number describing how crowded the whole park is on one open day.
_Avoid_: Busyness, attendance, crowdedness

**Quiet day**:
An open day whose actual crowd level lies in the bottom quarter of its season's open days.
_Avoid_: Empty day, low day

## Holidays

**Catchment**:
The regions whose residents make up the park's visitors: the German states, the French régions and nearby Swiss cantons.
_Avoid_: Market, source region

**Catchment region**:
One region of the catchment. A French région takes the school holidays of the zone it lies in.
_Avoid_: Holiday zone (for weighting)

**Catchment weight**:
How much a catchment region counts in holiday pressure, given its population and its distance from the park.

**Decay length**:
The distance at which a catchment region's weight falls to about 37% of what it would be at the park.
_Avoid_: Lambda, range

**Holiday pressure**:
The weighted share of the catchment that is on holiday on a given day. It comes in two kinds: school-holiday pressure and public-holiday pressure.
_Avoid_: Holiday score, holiday index

**Holiday block**:
One uninterrupted run of school-holiday days in one region, such as the Baden-Württemberg summer holidays.

**Long weekend**:
A weekend joined to a public holiday on the Friday before or the Monday after.

## Evaluation

**Season ranking**:
All open days of one season, ordered by predicted crowd level.

**Visit window**:
A set of open days a visitor is restricted to, such as "Saturdays in August", "the autumn holidays" or a calendar season like "spring".
_Avoid_: Season (for calendar spring, summer, autumn, winter)

**Window ranking**:
The open days inside one visit window, ordered by predicted crowd level.

**Advance information**:
Anything knowable before the predicted season starts, such as calendars, holidays and announced events.
_Avoid_: Known features, future-safe data

**Quiet-day precision**:
The share of predicted quiet days in a season ranking that were actual quiet days.

**Regret**:
How many crowd-level points the predicted quietest day of a visit window was above the window's actual quietest day.

**Test season**:
A season predicted from all earlier seasons to measure the model.

**Validation season**:
The last training season of a run, used to tune choices without touching the test season.

**Holdout season**:
Summer 2026, kept unseen until the final evaluation. Winter has no holdout season.
_Avoid_: Test set

**Savvy-visitor baseline**:
A fixed rule that calls weekends and holidays busy and every other open day quiet.
_Avoid_: Heuristic, naive model

**Last-season baseline**:
A prediction that copies last season's crowd level on the day with the same week number and weekday.
_Avoid_: Persistence model

**Upper-bound experiment**:
A run that adds information unavailable in advance, such as actual weather, to measure how much it would help.
_Avoid_: Oracle model, cheat run

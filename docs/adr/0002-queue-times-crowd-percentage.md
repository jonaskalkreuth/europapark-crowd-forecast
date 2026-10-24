# The crowd level is the Queue-Times daily crowd percentage

No free source publishes Europa-Park attendance, and per-ride wait history sits behind a bot challenge we chose not to bypass. The daily crowd percentage on the Queue-Times.com month calendar (https://queue-times.com/parks/51/calendar/YYYY/MM) is the only free history, so it is the crowd level.

## Consequences

- The percentage is a rank against all of the park's days, not attendance. This suits our evaluation, which ranks days within a season.
- Queue-Times says the percentage may consider factors beyond queue times, possibly weather. This could inflate the upper-bound experiment.
- The scraper fetches each month page once, slowly, and caches the raw HTML locally. Neither the HTML nor the scraped table is committed. The README credits "Powered by Queue-Times.com" with a link.

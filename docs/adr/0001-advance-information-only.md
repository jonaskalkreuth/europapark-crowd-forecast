# The main model uses advance information only

Each season is predicted as a whole, before it starts, so the main model may use only advance information: calendars, holidays and announced events. Actual weather is not known that far ahead, so it appears only in a separate upper-bound experiment that measures how much perfect weather knowledge would add.

## Considered Options

- **Actual weather as a feature**: rejected. It leaks information that a visitor planning ahead never has.
- **Opening hours as a feature**: rejected. The park may extend hours on days it expects to be busy, so hours partly reflect the crowd. Recent seasons also show the same hours every day. Hours only mark which days are open.

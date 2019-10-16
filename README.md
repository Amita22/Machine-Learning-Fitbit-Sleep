# Fitbit sleep duration analysis

Analyzes my own fitbit sleep data and creates a linear regression model to
study which fitbit parameters (physical activity, daily temperature) most affect sleep duration

Files or directories required for code to run:
- LukeKippenbrock/user-site-export: Directory with all my data (JSON format) exported from fitbit website
- Processed_Data: Directory where processed fitbit data is stored
- vacation_dates.py: Lists date ranges when I was not in Seattle.  This file is used to exclude dates from the analysis.
- SeattleWeather.csv: Contains weather data from Seattle, obtained from NOAA (National Oceanic and Atmospheric Administration) website

# The Question
How does the optimal electricity supply mix 
for a data center change 
with different generation capacities and carbon prices 
while minimizing the total cost?

# How to Run?
   1) Open the project folder in the terminal
   2) Install the required Python packages: Type `pip install -r requirements.txt` in the terminal
   3) Run the program: Type `python main.py` in the terminal
   4) Enter the values that you want to use
      Example: 
         Select date (MM-DD): 08-27
         Carbon price [EUR/tCO2] (default 200): 200
         Gas turbine capacity [MW] (default 100): 100
         Coal capacity [MW] (default 10): 10
   5) After a few seconds, figures with four different time resolutions will be generated.
      Open the generated figure files to view the results. The figures are not displayed automatically.
      If you select a date,
      ~day.png shows the data for the selected date,
      ~month.png shows the data for the corresponding month,
      ~season.png shows the data for the corresponding season,
      and ~year.png shows the yearly data.

# What the Numbers Mean?
   1) Total Generation [MWh]
      The total amount of electricity supplied by all energy sources during the selected period.
   2) Total Cost [EUR]
      The total cost of supplying electricity during the selected period.
      It includes both generation costs and carbon costs.
   3) Total CO2 Emissions [tCO2]
      The total CO2 emissions from all energy sources during the selected period.
   4) Grid Share [%]
      The percentage of total electricity demand supplied by the grid.
   5) Generation by Energy Source [MWh]
      The amount of electricity supplied by each energy source.
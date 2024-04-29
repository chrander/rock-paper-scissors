import numpy as np
import pandas as pd

from bokeh.io import curdoc
from bokeh.layouts import column, row
from bokeh.models import ColumnDataSource, NumericInput
from bokeh.plotting import figure

from rps.database.client import DatabaseClient
from rps.constants import DATABASE_URI


# Database
db_client = DatabaseClient(database_uri=DATABASE_URI)

# Set up data

x = np.array([])
y = np.array([])
source = ColumnDataSource(data=dict(x=x, y=y))


# Set up plot
plot = figure(height=600, width=1200, title="Human Winning Percentage",
              tools="crosshair,pan,reset,save,wheel_zoom",
              y_range=[-0.05, 1.05], x_axis_label="Round", 
              y_axis_label="Winning Percentage")

plot.line('x', 'y', source=source, line_width=3, line_alpha=0.6)


# Set up widgets
game_id_input = NumericInput(title="Game ID", value=1)

# Set up callbacks
def update_data(attrname, old, new) -> None:
    # Get the current Game ID values
    game_id = game_id_input.value
    df = pd.read_sql(f"SELECT round_id, outcome FROM rounds WHERE game_id = {game_id}", con=db_client.engine)
    df['win_count'] = (df.outcome == 'WIN').cumsum()
    df['loss_count'] = (df.outcome == 'LOSS').cumsum()
    df['win_pct'] = df.win_count / (df.win_count + df.loss_count)
    print(df)

    # Generate the new curve
    x = df.round_id.tolist()
    y = df.win_pct.tolist()

    source.data = dict(x=x, y=y)

game_id_input.on_change('value', update_data)

# Set up layouts and add to document
inputs = column(game_id_input)

curdoc().add_root(row(inputs, plot, width=1200))
curdoc().title = "Rock, Paper, Scissors Outcomes"

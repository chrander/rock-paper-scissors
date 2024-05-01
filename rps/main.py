import logging

from bokeh.io import curdoc
from bokeh.layouts import column, row
from bokeh.models import ColumnDataSource, NumericInput
from bokeh.plotting import figure
import numpy as np
import pandas as pd

from rps.database.client import DatabaseClient
from rps.constants import DATABASE_URI


logger = logging.getLogger(__name__)


def get_data(game_id: int) -> pd.DataFrame:
    win_pct_df = pd.read_sql(f"SELECT outcome FROM rounds WHERE game_id = {game_id}",
                             con=db_client.engine)
    win_pct_df["win_count"] = (win_pct_df.outcome == "WIN").cumsum()
    win_pct_df["loss_count"] = (win_pct_df.outcome == "LOSS").cumsum()
    win_pct_df["draw_count"] = (win_pct_df.outcome == "DRAW").cumsum()
    win_pct_df["win_pct"] = win_pct_df.win_count / (win_pct_df.win_count + win_pct_df.loss_count)
    win_pct_df["win_pct"].fillna(0.0)
    win_pct_df["round"] = np.arange(len(win_pct_df)) + 1

    outcome_df = pd.read_sql("SELECT win_count, loss_count, draw_count, "
                             "win_count+loss_count+draw_count AS games_count "
                             f"FROM game_stats WHERE game_id = {game_id}",
                             con=db_client.engine)
    outcome_df["x"] = 0
    outcome_df["y"] = 0

    # TODO: get player choice data and display it
    # p1_df = pd.read_sql("SELECT player1_choice AS p1_choice," \
    #                     "COUNT(playe1_choice) AS p1_count FROM rounds WHERE " \
    #                     f"game_id = {game_id} GROUP BY player1_choice", con=db_client.engine)

    return win_pct_df, outcome_df


# Database
db_client = DatabaseClient(database_uri=DATABASE_URI)

# Get the most recent game to start
most_recent_game = db_client.select_most_recent_game()

# Set up data
win_pct_df, outcome_df = get_data(most_recent_game.game_id)
win_pct_source = ColumnDataSource(data=win_pct_df)
outcome_source = ColumnDataSource(data=outcome_df)

# Set up plot
TOOLTIPS = """
    <font face="Arial" size="6"><strong>Round:</strong> @round</font><br>
    <font face="Arial" size="6"><strong>Winning Pct.:</strong> @win_pct{0.000}</font>
"""

wp_plot = figure(height=600, width=2200, title="Human Win Fraction Over Time",
                 tools="xpan,xwheel_zoom,reset,hover", tooltips=TOOLTIPS,
                 active_scroll="xwheel_zoom",
                 y_range=[-0.05, 1.05], x_axis_label="Round",
                 y_axis_label="Human Win Fraction", toolbar_location="above")

wp_plot.line(x="round", y="win_pct", source=win_pct_source, line_width=8, line_alpha=0.6)
wp_plot.toolbar.logo = None
wp_plot.axis.axis_line_width = 3
wp_plot.axis.axis_label_text_font_style = "bold"
wp_plot.axis.axis_label_text_font_size = "28pt"
wp_plot.axis.major_label_text_font_size = "24pt"
wp_plot.title.align = "center"
wp_plot.title.text_color = "navy"
wp_plot.title.text_font_size = "44pt"

figure_args = {
    "height": 550,
    "width": 550,
}

text_args = {
    "x": "x",
    "y": "y",
    "source": outcome_source,
    "text_font_size": "200pt",
    "text_align": "center",
    "text_baseline": "middle",
    "text_font_style": "bold"
}

games_plot = figure(title="Rounds", **figure_args)
games_plot.text(text="games_count", text_color="black", **text_args)

wins_plot = figure(title="Human Wins", **figure_args)
wins_plot.text(text="win_count", text_color="green", **text_args)

losses_plot = figure(title="Computer Wins", **figure_args)
losses_plot.text(text="loss_count", text_color="red", **text_args)

draws_plot = figure(title="Draws", **figure_args)
draws_plot.text(text="draw_count", text_color="blue", **text_args)

for p in [games_plot, wins_plot, losses_plot, draws_plot]:
    p.xaxis.visible = False
    p.yaxis.visible = False
    p.xgrid.visible = False
    p.ygrid.visible = False
    p.toolbar_location = None
    p.title.align = "center"
    p.title.text_color = "navy"
    p.title.text_font_size = "44pt"


# Set up callbacks
def update_data_on_game_id_change(attrname, old, new) -> None:
    """Update when game ID input changes"""
    update_data()


def update_data() -> None:
    # Get the current Game ID values
    win_pct_df, outcome_df = get_data(game_id_input.value)
    win_pct_source.data = win_pct_df
    outcome_source.data = outcome_df
    logger.debug("Updated data")


# Set up widgets
game_id_input = NumericInput(title="Game ID", value=most_recent_game.game_id)
game_id_input.on_change('value', update_data_on_game_id_change)

# Set up layouts and add to document
inputs_col = column(game_id_input)
win_pct_row = row(wp_plot)
outcome_row = row(games_plot, wins_plot, losses_plot, draws_plot)
plot_col = column(outcome_row, win_pct_row)
final_row = row(inputs_col, plot_col)

curdoc().title = "Rock, Paper, Scissors!"
curdoc().add_periodic_callback(update_data, 3000)
curdoc().add_root(final_row)

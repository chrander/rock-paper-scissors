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

COLORS = {
    "PAPER": "#ece7f2",
    "ROCK": "#9ebcda",
    "SCISSORS": "#8856a7",
    "WIN": "green",
    "LOSS": "firebrick"
}


def get_data(game_id: int) -> pd.DataFrame:
    win_pct_df = pd.read_sql(f"SELECT outcome FROM rounds WHERE game_id = {game_id}",
                             con=db_client.engine)
    win_pct_df["win_count"] = (win_pct_df.outcome == "WIN").cumsum()
    win_pct_df["loss_count"] = (win_pct_df.outcome == "LOSS").cumsum()
    win_pct_df["draw_count"] = (win_pct_df.outcome == "DRAW").cumsum()
    win_pct_df["win_pct"] = win_pct_df.win_count / (win_pct_df.win_count + win_pct_df.loss_count)
    win_pct_df["win_pct"].fillna(0.0)
    win_pct_df["round"] = np.arange(len(win_pct_df)) + 1

    # Get outcome data
    outcome_df = pd.read_sql("SELECT win_count, loss_count, draw_count, "
                             "win_count+loss_count+draw_count AS games_count "
                             f"FROM game_stats WHERE game_id = {game_id}",
                             con=db_client.engine)
    outcome_df["x"] = 0
    outcome_df["y"] = 0

    # Get player choice data
    choices_df = pd.read_sql("SELECT timestamp, player1_choice AS p1, player2_choice AS p2, "
                             f"outcome FROM rounds WHERE game_id = {game_id} "
                             "ORDER BY timestamp DESC LIMIT 10",
                             con=db_client.engine)

    choices_df["p1_color"] = choices_df.p1.apply(lambda x: COLORS[x])
    choices_df["p2_color"] = choices_df.p2.apply(lambda x: COLORS[x])

    choices_df["p1_line_color"] = choices_df.outcome.apply(
        lambda x: COLORS["WIN"] if x == "WIN" else COLORS["LOSS"])
    choices_df["p2_line_color"] = choices_df.outcome.apply(
        lambda x: COLORS["LOSS"] if x == "WIN" else COLORS["WIN"])

    choices_df = choices_df.sort_values("timestamp", ascending=True)
    choices_df["x"] = np.arange(len(choices_df))
    choices_df["y"] = np.zeros(len(choices_df))

    return win_pct_df, outcome_df, choices_df


# Database
db_client = DatabaseClient(database_uri=DATABASE_URI)

# Get the most recent game to start
most_recent_game = db_client.select_most_recent_game()

# Set up data
win_pct_df, outcome_df, choices_df = get_data(most_recent_game.game_id)
win_pct_source = ColumnDataSource(data=win_pct_df)
outcome_source = ColumnDataSource(data=outcome_df)
choices_source = ColumnDataSource(data=choices_df)

# ---------------------------- #
# Set up Winning Fraction plot #
TOOLTIPS = """
    <font face="Arial" size="6"><strong>Round:</strong> @round</font><br>
    <font face="Arial" size="6"><strong>Winning Pct.:</strong> @win_pct{0.000}</font>
"""

wp_plot = figure(height=600, width=2200, title="Human Win Fraction Over Time",
                 tools="xpan,xwheel_zoom,reset,hover", tooltips=TOOLTIPS,
                 active_scroll="xwheel_zoom",
                 y_range=[-0.05, 1.05], x_axis_label="Round",
                 y_axis_label="Human Win Fraction", toolbar_location="above",
                 margin=(20, 20, 20, 20))

wp_plot.line(x="round", y="win_pct", source=win_pct_source, line_width=8, line_alpha=0.6)
wp_plot.toolbar.logo = None
wp_plot.axis.axis_line_width = 3
wp_plot.axis.axis_label_text_font_style = "bold"
wp_plot.axis.axis_label_text_font_size = "28pt"
wp_plot.axis.major_label_text_font_size = "24pt"
wp_plot.title.align = "center"
wp_plot.title.text_color = "navy"
wp_plot.title.text_font_size = "44pt"

# ---------------------------- #
# Set up "scoreboard" plots
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

# ---------------------------- #
# Set up recent choices plot

c1 = figure(height=200, width=2200, y_range=(-0.6, 0.6), title="Most Recent Human Choices",
            margin=(20, 20, 20, 20))
c1.rect(x="x", y="y", fill_color="p1_color", line_color="p1_line_color", source=choices_source,
        width=0.92, height=1, fill_alpha=0.6, line_width=7)
c1.text(x="x", y="y", text="p1", source=choices_source, text_align="center",
        text_baseline="middle", text_font_size="22pt", text_font_style="bold")

c2 = figure(height=200, width=2200, y_range=(-0.6, 0.6), title="Most Recent Computer Choices",
            margin=(20, 20, 20, 20))
c2.rect(x="x", y="y", fill_color="p2_color", line_color="p2_line_color", source=choices_source,
        width=0.92, height=1, fill_alpha=0.6, line_width=7)
c2.text(x="x", y="y", text="p2", source=choices_source, text_align="center",
        text_baseline="middle", text_font_size="22pt", text_font_style="bold")

for p in [c1, c2]:
    p.xaxis.visible = False
    p.yaxis.visible = False
    p.xgrid.visible = False
    p.ygrid.visible = False
    p.toolbar_location = None
    p.outline_line_color = None
    p.title.align = "center"
    p.title.text_color = "navy"
    p.title.text_font_size = "24pt"



# Set up callbacks
def update_data_on_game_id_change(attrname, old, new) -> None:
    """Update when game ID input changes"""
    update_data()


def update_data() -> None:
    # Get the current Game ID values
    win_pct_df, outcome_df, choices_df = get_data(game_id_input.value)
    win_pct_source.data = win_pct_df
    outcome_source.data = outcome_df
    choices_source.data = choices_df
    logger.debug("Updated data")


# Set up widgets
game_id_input = NumericInput(title="Game ID", value=most_recent_game.game_id)
game_id_input.on_change('value', update_data_on_game_id_change)

# Set up layouts and add to document
inputs_col = column(game_id_input)
win_pct_row = row(wp_plot)
outcome_row = row(games_plot, wins_plot, losses_plot, draws_plot)
plot_col = column(outcome_row, win_pct_row, c1, c2)
final_row = row(inputs_col, plot_col)

curdoc().title = "Rock, Paper, Scissors!"
curdoc().add_periodic_callback(update_data, 3000)
curdoc().add_root(final_row)

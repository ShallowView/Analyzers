from sqlalchemy import create_engine
from urllib.parse import quote_plus
from dataAnalyste.analysis_functions import *
from DataCollection.ProcessPGN import insertDataToPostgres




# Function to create a secure connection to the database
def get_engine(params):
    ssl_args = {
        "sslmode": params["sslmode"],
        "sslcert": params["sslcert"],
        "sslkey": params["sslkey"],
        "sslrootcert": params["sslrootcert"]
    }

    ssl_query = "&".join([f"{key}={quote_plus(val)}" for key, val in ssl_args.items()])

    url = (
        f"postgresql+psycopg2://{params['user']}:{params['password']}@"
        f"{params['host']}:{params['port']}/{params['dbname']}?{ssl_query}"
    )

    return create_engine(url)

""" Connect to database """
engine = get_engine(db_params_SSL)
""" Run All Analyses """

if __name__ == "__main__":
    print("Running MaxElo vs Current Elo analysis...")
    elo_df = get_max_vs_current_elo(engine)
    #plot_max_vs_current_elo(elo_df)
    df_max_current = get_max_vs_current_elo(engine)
    #insertDataToPostgres(db_params_SSL, 'max_vs_current_elo', df_max_current)

    print("Running win rate by title analysis...")
    title_df = get_win_rate_by_title(engine)
    #plot_win_rate_by_title(title_df)
    df_win_title = get_win_rate_by_title(engine)
    insertDataToPostgres(db_params_SSL, 'wr_title', df_win_title)

    print("Running win rate by color analysis...")
    color_df = get_win_rate_by_color(engine)
    print(color_df.head)
    #plot_win_rate_by_color(color_df)
    df_color = get_win_rate_by_color(engine)
    insertDataToPostgres(db_params_SSL, 'wr_color', df_color)

    print("Running average Elo by opening analysis...")
    opening_df = get_avg_elo_by_opening(engine)
    #plot_avg_elo_by_opening(opening_df)
    df_opening = get_avg_elo_by_opening(engine)
    insertDataToPostgres(db_params_SSL, 'avg_elo_by_opening', df_opening)

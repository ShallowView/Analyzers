from __init__ import *



# Database connection parameters
db_params_SSL = {
    "dbname": "shallowview",
    "user": "user", # Replace with your database username
    "password": "", # Replace with your database password
    "host": "s0.net.pimous.dev",
    "port": 31003,
    "sslmode": "require",  # Enforce SSL connection
    "sslcert": ".crt",  # Path to client certificate
    "sslkey": ".key",    # Path to client private key
    "sslrootcert": ".chain.crt"   # Path to CA certificate
}


""" Connect to database """
engine = get_engine(db_params_SSL)


""" Run All Analyses """
if __name__ == "__main__":


    print("Running win rate by title analysis...")
    title_df = get_win_rate_by_title(engine)
    plot_win_rate_by_title_json(title_df)

    print("Running win rate by color analysis...")
    color_df = get_win_rate_by_color(engine)
    plot_win_rate_by_color_json(color_df)

    print("Running average Elo by opening analysis...")
    opening_df = get_avg_elo_by_opening(engine)
    plot_avg_elo_by_opening_json(opening_df)

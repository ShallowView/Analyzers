import logging

import psycopg
import pandas as pd

def getPlayersOpenings(connection_params : dict) -> pd.DataFrame:
	try:
		with psycopg.connect(**connection_params) as conn:
			with conn.cursor() as cursor:
				from_query = """
					with player_games as (
					select p.id as player_id, count(*) as total_games
					from players p
					join public.games g on p.id = g.white
					group by p.id
				)
				select
					p.name as player_name,
					o.name as opening_name,
					count(*) as times_played,
					round((count(*)::decimal / pg.total_games), 2) as percentage_played
				from players p
				join public.games g on p.id = g.white
				join public.openings o on o.id = g.opening
				join player_games pg on p.id = pg.player_id
				group by p.name, o.name, pg.total_games
				having count(*) >= 100 and (count(*)::decimal / pg.total_games) >= 0.01
				order by times_played desc; 
				"""
				cursor.execute(from_query)
				result = cursor.fetchall()
				return pd.DataFrame(result, columns=[desc[0] for desc in cursor.description])
	except Exception as e:
		logging.error(e)
		return pd.DataFrame()



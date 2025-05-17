import os
import sys

from JSON_handling import validate_and_extract_params
from __init__ import *
from json import load

# Names of the tables in the database
tables = {
	"games": "games",
	"players": "players",
	"openings": "openings"
}

if __name__ == "__main__":
	def main():
		args = sys.argv[1:]
		if not args:
			raise ValueError("Please provide a JSON file path as an argument.")
		for arg in args:
			if not os.path.isfile(arg):
				raise ValueError(f"File {arg} does not exist.")
			with open(arg, 'r') as file:
				all_params = load(file)

				if all_params.get("pgn_files_dir") is None:
					raise ValueError("Please provide a directory for PGN files.")

				required_db_keys = ["dbname", "user", "host", "port"]
				optional_db_keys = ["password", "sslmode", "sslkey", "sslcert",
														"sslrootcert"]
				db_params = validate_and_extract_params(all_params, required_db_keys,
																								optional_db_keys)

				setMaxCores()

				if all_params.get("openings_dir"):

					lichessOpeningTSVs = [os.path.join(all_params["openings_dir"], f) for
																f in os.listdir(all_params["openings_dir"]) if
																os.path.isfile(
																	os.path.join(all_params["openings_dir"], f)
																)]
					addOpeningsToDatabase(lichessOpeningTSVs, db_params, tables)

				PGNFiles = [os.path.join(all_params["pgn_files_dir"], f) for f in
										os.listdir(all_params["pgn_files_dir"]) if
										os.path.isfile(
											os.path.join(all_params["pgn_files_dir"], f)
										)]

				addNewPGNtoDatabase(PGNFiles, db_params, tables)


	main()

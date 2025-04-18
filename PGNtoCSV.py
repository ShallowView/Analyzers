import io

import pandas as pd



def process_pgn(file : str, output : str) -> None:
    count = 0
    games = []
    dic = {}
    with open(file, "r") as f:
        for line in f.readlines():
            if line.startswith("["):
                string = line[1:-1]
                header = string.split()[0]
                dic[header] = string[len(header):-2].strip().strip('"')
            else:
                if len(dic)!=0:  # Append only non-empty dictionaries
                    games.append(dic)
                    count += 1
                dic = {}
    print(f"Number of games: {count}")

    # Create a DataFrame
    df = pd.DataFrame(games)

    # Save to CSV
    df.to_csv(output, index=False)


def count_games(file : io.TextIOBase) -> int:
    """
    Count the number of games in a PGN file.
    """
    count = 0
    for line in file:
        if line.startswith("[Event"):
            count += 1
    return count
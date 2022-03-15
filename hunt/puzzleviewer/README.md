# Puzzleviewer
A utility to browse all puzzles and solutions. It bypasses the database and whether a team has access to the puzzle, so that puzzles can be tested and fact-checked without worrying about hunt state.

To access puzzleviewer, you must be logged in as a internal or admin team (as defined in [teams.tsv](../data/hunt_info/teams.tsv).

To enable puzzleviewer, you must set `HUNT_PUZZLEVIEWER_ENABLED = True` in settings. Be careful setting this for production, as it serves puzzles inefficiently. However, there isn't really an issue using it, as access is still authenticated through Django users.

Some special puzzles will not work through puzzleviewer. Puzzle subviews also won't work.

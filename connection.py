import os
import psycopg2 as pp
import psycopg2.extras as ppx


def get_host():
    """
    If PGHOST is unset, raise SystemExit
    :returns: Returns a hostname (str) that runs postgres.
    """
    host = os.getenv("PGHOST")
    if host is None:
        raise SystemExit("Please set the PGHOST environment")
    return host


def get_brew_channels():
    """
    :returns: Returns a list of rows. Each row is accessible by dictionary
              keys.
    """
    host = get_host()
    conn = pp.connect(dbname="public", host=host, port=5433)
    cur = conn.cursor(cursor_factory=ppx.DictCursor)

    # Select rows from brew channel table. Contains channel IDs
    # and channel names
    postgreSQL_select_Query = "SELECT * FROM brew.channels;"
    # Execute Query
    cur.execute(postgreSQL_select_Query)

    # Selecting rows from brew.task.id table using cursor.fetchall
    return cur.fetchall()


if __name__ == "__main__":

    brew_channels = get_brew_channels()
    print(brew_channels)

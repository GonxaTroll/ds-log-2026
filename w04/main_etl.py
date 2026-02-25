"""main_etl.py
Main ETL script to build the anime database and store all information for a given anime ID,
including related shows.
"""
import time
import duckdb
from tqdm import tqdm

from config.config import ANIME_DB_PATH
from db.build_db import build_anime_db
from db.update import upsert_show_info, upsert_episodes, upsert_reviews, upsert_forum_messages
from scraper import AnimeScraperFormatterDF


def store_all_anime_info(anime_id: int):
    """Recursively store all information for a given anime ID, including related shows."""
    anime_conn = duckdb.connect(database = ANIME_DB_PATH)
    anime_client = AnimeScraperFormatterDF(anime_id)
    # Get info:
    if anime_conn.execute(f"select * from show_info where id = {anime_id}").df().empty or\
       anime_conn.execute(f"select * from show_genres where show_id = {anime_id}").df().empty or\
       anime_conn.execute(f"select * from show_themes where show_id = {anime_id}").df().empty or\
       anime_conn.execute(f"select * from show_relationships where source_id = {anime_id}").df()\
        .empty:
        info, genres, themes, relations  = anime_client.get_full_payload()
        upsert_show_info(anime_conn, info, genres, themes, relations)
    # Get episodes:
    if anime_conn.execute(f"select * from anime_episodes where anime_id = {anime_id}").df().empty:
        episodes = anime_client.get_episodes()
        upsert_episodes(anime_conn, episodes)
    # Get reviews:
    if anime_conn.execute(f"select * from reviews where anime_id = {anime_id}").df().empty:
        reviews, reactions, _ = anime_client.get_reviews(preliminary = True, spoilers = True)
        upsert_reviews(anime_conn, reviews, reactions)
    # Get forum messages:
    missing_forum_episodes = anime_conn.execute("""
                    select e.*
                    from anime_episodes as e
                    left join forum_messages as f on e.forum_topic_id = f.forum_id
                    where f.forum_id is null
                    """).df()["forum_topic_id"].tolist()
    for forum_topic_id in tqdm(missing_forum_episodes, desc="Fetching forum messages"):
        forum_messages = anime_client.get_forum_messages(forum_topic_id)
        upsert_forum_messages(anime_conn, forum_messages)
        time.sleep(1)

    # Get info on related shows and retrieve all its info as well:
    missing_related_shows = anime_conn.execute("""
                   select r.*
                   from show_relationships as r
                   left join show_info as s on r.id = s.id
                   where r.type = 'anime' and s.title is null
                   """).df()["id"].tolist()
    for related_show_id in tqdm(missing_related_shows, desc="Fetching related shows"):
        store_all_anime_info(related_show_id) # Recursively store info for related shows
        time.sleep(5)


def main(anime_id: int):
    """Main function to build the database and store all information for a given anime ID,
       including related shows.

    Args:
        anime_id (int): Anime ID.
    """
    build_anime_db()
    store_all_anime_info(anime_id)

if __name__ == "__main__":
    main(anime_id = 54492)

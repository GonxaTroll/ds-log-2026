import pandas as pd

def upsert_show_info(anime_conn, info: pd.DataFrame, genres: pd.DataFrame,
                     themes: pd.DataFrame, relations: pd.DataFrame):
    assert isinstance(info, pd.DataFrame) and isinstance(genres, pd.DataFrame) and\
        isinstance(themes, pd.DataFrame) and isinstance(relations, pd.DataFrame)

    upsert_info = """
        INSERT INTO show_info
            SELECT * FROM info
        ON CONFLICT (id, type)
        DO UPDATE SET
            -- title = excluded.title,
            -- title_english = excluded.title_english,
            -- title_japanese = excluded.title_japanese,
            -- source = excluded.source,
            -- aired_from = excluded.aired_from,
            -- duration = excluded.duration,
            episodes = excluded.episodes,
            aired_to = excluded.aired_to,
            rating = excluded.rating,
            score = excluded.score,
            scored_by = excluded.scored_by,
            rank = excluded.rank,
            popularity = excluded.popularity,
            members = excluded.members,
            favorites = excluded.favorites
    """

    upsert_genres =\
        """
        insert into show_genres
        select
            show_id,
            id,
            name,
            type
        from genres
        on conflict (show_id, id)
        do update set
            name = excluded.name,
            type = excluded.type
        """

    upsert_themes =\
        """
        insert into show_themes
        select
            show_id,
            id,
            name,
            type
        from themes
        on conflict (show_id, id)
        do update set
            name = excluded.name,
            type = excluded.type
        """

    upsert_relations =\
        """
        insert into show_relationships
        select
            source_id,
            id,
            type,
            relation
        from relations
        on conflict (source_id, id)
        do update set
            type = excluded.type,
            relation = excluded.relation
        """

    anime_conn.execute(upsert_info)
    anime_conn.execute(upsert_genres)
    anime_conn.execute(upsert_themes)
    anime_conn.execute(upsert_relations)

def upsert_episodes(anime_conn, episodes: pd.DataFrame):
    assert isinstance(episodes, pd.DataFrame)
    query = """
        insert into anime_episodes
        select
            anime_id,
            id,
            title,
            title_japanese,
            aired,
            score,
            filler,
            recap,
            forum_topic_id
        from episodes
        on conflict (anime_id, id) do update set
            title = excluded.title,
            title_japanese = excluded.title_japanese,
            aired = excluded.aired,
            score = excluded.score,
            filler = excluded.filler,
            recap = excluded.recap,
            forum_topic_id = excluded.forum_topic_id;
    """
    anime_conn.execute(query)


def upsert_reviews(anime_conn, reviews_df: pd.DataFrame, review_reactions_df: pd.DataFrame):
    assert isinstance(reviews_df, pd.DataFrame) and isinstance(review_reactions_df, pd.DataFrame)
    query_reviews =\
        """
        insert into reviews
        select
            anime_id,
            id,
            type,
            review,
            score,
            tags,
            is_spoiler,
            is_preliminary,
            username,
            date
        from reviews_df
        on conflict (anime_id, id) do update set
            review = excluded.review,
            score = excluded.score,
            tags = excluded.tags,
            is_spoiler = excluded.is_spoiler,
            is_preliminary = excluded.is_preliminary,
            username = excluded.username,
            date = excluded.date;
        """

    query_reactions =\
        """
        insert into review_reactions
        select
            anime_id,
            id,
            overall,
            nice,
            love_it,
            funny,
            confusing,
            informative,
            well_written,
            creative
        from review_reactions_df
        on conflict (anime_id, id) do update set
            overall = excluded.overall,
            nice = excluded.nice,
            love_it = excluded.love_it,
            funny = excluded.funny,
            confusing = excluded.confusing,
            informative = excluded.informative,
            well_written = excluded.well_written,
            creative = excluded.creative;
        """
    anime_conn.execute(query_reviews)
    anime_conn.execute(query_reactions)


def upsert_forum_messages(anime_conn, forum_messages_df: pd.DataFrame):
    assert isinstance(forum_messages_df, pd.DataFrame)

    forum_query =\
    """
    insert into forum_messages
    select
        show_id,
        forum_id,
        id,
        user,
        datetime,
        replied_id,
        content,
        additional_media
    from forum_messages_df
    on conflict (show_id, forum_id, id) do update set
        user = excluded.user,
        datetime = excluded.datetime,
        replied_id = excluded.replied_id,
        content = excluded.content,
        additional_media = excluded.additional_media;
    """
    anime_conn.execute(forum_query)


def upsert_anime_statistics(anime_conn, statistics_df: pd.DataFrame) -> None:
    assert isinstance(statistics_df, pd.DataFrame)
    statistics_query =\
        """
        insert into anime_statistics
        select
            anime_id,
            kpi_name,
            kpi_value,
            amount
        from statistics_df
        on conflict (anime_id, kpi_name, kpi_value) do update set
            amount = excluded.amount;
        """
    anime_conn.execute(statistics_query)

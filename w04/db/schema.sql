create table if not exists show_info (
    id integer,
    type varchar,
    title varchar,
    title_english varchar,
    title_japanese varchar,
    source varchar,
    episodes integer,
    aired_from date,
    aired_to date,
    duration varchar,
    rating varchar,
    score float,
    scored_by integer,
    rank integer,
    popularity integer,
    members integer,
    favorites integer,
    primary key (id, type)
);


create table if not exists show_relationships (
    source_id integer,
    id integer,
    type varchar,
    relation varchar,
    primary key (source_id, id)
);

create table if not exists show_genres (
    show_id integer,
    id integer,
    name varchar,
    type varchar,
    primary key (show_id, id)
);

create table if not exists show_themes (
    show_id integer,
    id integer,
    name varchar,
    type varchar,
    primary key (show_id, id)
);

create table if not exists anime_episodes (
    anime_id integer,
    id integer,
    title varchar,
    title_japanese varchar,
    aired date,
    score float,
    filler boolean,
    recap boolean,
    forum_topic_id integer,
    primary key (anime_id, id)
);

create table if not exists reviews (
    anime_id integer,
    id integer,
    type varchar,
    review text,
    score float,
    tags varchar [],
    is_spoiler boolean,
    is_preliminary boolean,
    username varchar,
    date datetime,
    primary key (anime_id, id)
);

create table if not exists review_reactions (
    anime_id integer,
    id integer,
    overall integer,
    nice integer,
    love_it integer,
    funny integer,
    confusing integer,
    informative integer,
    well_written integer,
    creative integer,
    primary key (anime_id, id)
);

create table if not exists forum_messages (
    show_id integer,
    forum_id integer,
    id integer,
    user varchar,
    datetime datetime,
    replied_id integer,
    content varchar,
    additional_media integer,
    primary key (show_id, forum_id, id)
);

create table if not exists anime_statistics (
    anime_id integer,
    kpi_name varchar,
    kpi_value varchar,
    amount integer,
    primary key (anime_id, kpi_name, kpi_value)
);

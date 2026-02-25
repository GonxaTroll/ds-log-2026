import json
import re
import requests
import time
import traceback
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime

class MyAnimeListForumScraper:
    def __init__(self):
        self.form_url = "https://myanimelist.net/forum/?topicid={topic_id}"

    def _get_forum_pages(self, forum_topic):
        forum = requests.get(forum_topic, timeout = 10)
        forum = BeautifulSoup(forum.content, "lxml")
        pages = forum.find("div", class_ = "pages")
        pages = int(re.findall(r"Pages \((\d+)\)", pages.text)[0])
        return pages

    def _get_message_data(self, forum_topic):
        forum = requests.get(forum_topic, timeout = 10)
        forum = BeautifulSoup(forum.content, "lxml")
        messages = forum.find_all("div", class_="forum-topic-message message")
        messages = [
            message for message in messages if not message.find("div",
                                                                class_ = "message-wrapper stretch")
            ]
        return messages

    def format_message_data(self, message):
        message_id = int(message["data-id"])
        message_user = message["data-user"]

        # all_messages[-1].find("div", class_ = "date")
        message_datetime = pd.to_datetime(
            datetime.fromtimestamp(
                int(message.find("div", class_ = "date")["data-time"])
                )
            )

        message_content = message.find("div", class_ = "content")
        message_replied_id = message_content.find("div", class_="replied-container")
        message_replied_id =\
            int(message_replied_id.find("div", class_ = "js-replyto-target")["data-id"])\
                if message_replied_id else None

        message_main_content = message_content.find("table", class_ = "body clearfix").text
        # message_post_actions = message_content.find("div", class_ = "postActions").text
        additional_media = 0
        sig_text = ""
        for sig_container in message_content.find_all("div", class_ = "sig-container"):
            additional_media += len(sig_container.find_all("a"))
            sig_text += sig_container.text
        if sig_text != "":
            message_main_content += f"\n\n{sig_text}"
        return {
            "id": message_id,
            "user": message_user,
            "datetime": message_datetime,
            "replied_id": message_replied_id,
            "content": message_main_content,
            "additional_media": additional_media,
        }

    def get_forum_raw_messages(self, topic_id):
        forum_url = f"https://myanimelist.net/forum/?topicid={topic_id}"
        pages = self._get_forum_pages(forum_url)
        messages = self._get_message_data(forum_url)
        n_messages = len(messages)
        pages_counter = 1
        while pages_counter < pages:
            pages_counter += 1
            messages.extend(
                self._get_message_data(forum_url + f"&show={n_messages * (pages_counter - 1)}")
            )
            time.sleep(1)  # to avoid rate limiting
        return messages

    def get_forum_messages(self, topic_id):
        raw_messages = self.get_forum_raw_messages(topic_id)
        formatted_messages = pd.DataFrame(
            [self.format_message_data(message) for message in raw_messages]
            )
        formatted_messages["forum_id"] = topic_id
        return formatted_messages


class ScraperRestClient:
    def __init__(self):
        pass
    def _get_raw_request(self, endpoint: str):
        response = requests.get(endpoint, timeout = 10)
        if response.status_code == 200:
            return response
        raise Exception(response.status_code,
                        f"Request to {endpoint} failed with status code {response.status_code}")

    def _parse_json_from_api(self, response: str):
        return json.loads(response.content)
    def get_parsed_json_from_api(self, endpoint: str):
        response = self._get_raw_request(endpoint)
        return self._parse_json_from_api(response)

class JikanClient(ScraperRestClient):
    def __init__(self):
        super().__init__()
        self.BASE_URL = "https://api.jikan.moe/v4"
    def get_parsed_json_from_api(self, endpoint: str):
        full_endpoint = f"{self.BASE_URL}{endpoint}"
        return super().get_parsed_json_from_api(full_endpoint)
    def get_all_pages_from_endpoint(self, endpoint: str):
        all_data = []
        page = 1
        has_next_page = True
        # requests_per_minute = 60
        # requests_per_second = 3
        # max_retries = 5
        # timer_seconds, timer_minutes = time.time(), time.time()
        endpoint_separator = "&" if "?" in endpoint else "?"
        while has_next_page:
            paged_endpoint = f"{endpoint}{endpoint_separator}page={page}"
            try:
                response = self.get_parsed_json_from_api(paged_endpoint)
                data = response.get("data", [])
                has_next_page = response.get("pagination", {}).get("has_next_page", True)
                time.sleep(1)  # to avoid rate limiting
            except:
                _, exc_value, _ = traceback.sys.exc_info()
                status_code = exc_value.args[0]
                if status_code == 429:
                    print("Rate limit exceeded. Waiting before retrying...")
                    time.sleep(60) # since we are not paralelizing, the 1 second wait is not necessary, we can just wait the full minute
                    continue
                else:
                    raise Exception(f"Failed to fetch page {page}.")
            if not data:
                break
            all_data.extend(data)
            page += 1
        return all_data

class AnimeScraper(JikanClient):
    def __init__(self, anime_id: int):
        super().__init__()
        self.anime_id = anime_id
        self.forum_scraper = MyAnimeListForumScraper()

    def get_full_payload(self):
        return self.get_parsed_json_from_api(f"/anime/{self.anime_id}/full")

    def get_episodes(self):
        episodes = pd.DataFrame(
            self.get_all_pages_from_endpoint(f"/anime/{self.anime_id}/episodes")
        )
        if episodes.empty:
            return pd.DataFrame(columns = ["anime_id", "id", "title", "title_japanese", "aired",
                                           "score", "filler", "recap", "forum_topic_id", "url",
                                           "title_romanji"])
        episodes["forum_topic_id"] = episodes["forum_url"].apply(
            lambda x: int(re.search(r'topicid=(\d+)', x).group(1))
        )
        episodes = episodes.drop(columns=["forum_url"])
        episodes["anime_id"] = self.anime_id
        return episodes

    def get_statistics(self):
        statistics = self.get_parsed_json_from_api(f"/anime/{self.anime_id}/statistics")["data"]
        statistics_df = []
        for kpi_value in statistics:
            if kpi_value != "scores":
                statistics_df.append({
                    "kpi_name": "watching_status",
                    "kpi_value": kpi_value,
                    "amount": statistics[kpi_value]
                })
            else:
                for score in statistics[kpi_value]:
                    statistics_df.append({
                        "kpi_name": "score",
                        "kpi_value": f"score_{score['score']}",
                        "amount": score["votes"]
                    })
        statistics_df = pd.DataFrame(statistics_df)
        statistics_df["anime_id"] = self.anime_id
        return statistics_df

    def _get_reviews_df(self, data):
        data_normalized = pd.json_normalize(data)

        # 1. Main Reviews
        reviews = pd.DataFrame(data).drop(columns=['reactions', 'user'])
        reviews["username"] = data_normalized['user.username']
        reviews["anime_id"] = self.anime_id

        # 2. Reactions (using mal_id as the foreign key)
        reaction_cols = [col for col in data_normalized if col.startswith('reactions.')]
        reactions = data_normalized[['mal_id'] + reaction_cols]
        reactions = reactions.rename(columns=lambda x: x.replace('reactions.', ''))
        reactions["anime_id"] = self.anime_id

        # 3. Users
        users = data_normalized[['user.username', 'user.url', 'user.images.jpg.image_url']]
        users = users.drop_duplicates(subset='user.username')
        return reviews, reactions, users

    def get_reviews(self, preliminary: bool = True, spoilers: bool = True):
        query_params = f"?preliminary={str(preliminary).lower()}&spoilers={str(spoilers).lower()}"
        data = self.get_all_pages_from_endpoint(f"/anime/{self.anime_id}/reviews{query_params}")
        return self._get_reviews_df(data)

    def get_user_updates(self):
        return self.get_all_pages_from_endpoint(f"/anime/{self.anime_id}/userupdates")

    def get_forum_messages(self, topic_id: int):
        forum_messages = self.forum_scraper.get_forum_messages(topic_id)
        forum_messages["anime_id"] = self.anime_id
        return forum_messages


class AnimeScraperFormatterDF(AnimeScraper):
    def __init__(self, anime_id: int):
        super().__init__(anime_id = anime_id)

    def get_full_payload(self):
        show_info = super().get_full_payload()["data"]

        columns = [
            "mal_id", "type", "title", "title_english", "title_japanese", "source", "episodes",
            "aired_from", "aired_to", "duration", "rating", "score", "scored_by", "rank",
            "popularity", "members", "favorites"
        ]

        # Initial info
        show_info_df = []
        for key in columns:
            if key in ["aired_from", "aired_to"]:
                show_info_df.append(show_info["aired"].get(key.split("_")[1], None))
            else:
                show_info_df.append(show_info.get(key, None))
        show_info_df = pd.DataFrame([show_info_df], columns = columns)

        for col in ["mal_id", "episodes", "score", "scored_by", "rank", "popularity", "members",
                    "favorites"]:
            show_info_df[col] = pd.to_numeric(show_info_df[col], errors = "coerce")
        for col in ["aired_from", "aired_to"]:
            show_info_df[col] = pd.to_datetime(show_info_df[col], errors = "coerce")

        # Genres
        columns = ["show_id", "id", "name", "type"]
        show_genres_df = pd.DataFrame(columns = columns)
        # https://myanimelist.net/anime/genre/8/Drama'
        for genre in show_info["genres"] + show_info["explicit_genres"]:
            row_genres = [show_info["mal_id"]]
            row_genres.append(genre["mal_id"])
            row_genres.append(genre["name"])
            row_genres.append(genre["type"])
            row_genres = pd.DataFrame([row_genres], columns = columns)
            show_genres_df = pd.concat([show_genres_df, row_genres], ignore_index = True)

        # Themes
        show_themes_df = pd.DataFrame(columns = columns)
        # https://myanimelist.net/anime/genre/13/Historical
        for theme in show_info["themes"]:
            row_themes = [show_info["mal_id"]]
            row_themes.append(theme["mal_id"])
            row_themes.append(theme["name"])
            row_themes.append(theme["type"])
            row_themes = pd.DataFrame([row_themes], columns = columns)
            show_themes_df = pd.concat([show_themes_df, row_themes], ignore_index = True)

        columns = ["source_id", "relation", "id", "type"]
        anime_relations_df = pd.DataFrame(columns = columns)
        for relation in show_info["relations"]:
            row_relations = [show_info["mal_id"]]
            row_relations.append(relation["relation"])
            entry = relation["entry"][0]
            row_relations.append(entry["mal_id"])
            row_relations.append(entry["type"])
            row_relations = pd.DataFrame([row_relations], columns = columns)
            anime_relations_df = pd.concat([anime_relations_df, row_relations], ignore_index = True)

        return show_info_df, show_genres_df, show_themes_df, anime_relations_df

    def get_episodes(self):
        anime_episodes = super().get_episodes()
        # 'https://myanimelist.net/anime/54492/Kusuriya_no_Hitorigoto/episode/1'
        anime_episodes = anime_episodes.rename(columns = {
            "mal_id": "id",
        }).drop(columns = ["url", "title_romanji"])

        columns = [
            "anime_id", "id", "title", "title_japanese", "aired", "score", "filler", "recap",
            "forum_topic_id"
        ]
        anime_episodes = anime_episodes[columns]
        anime_episodes["aired"] = pd.to_datetime(anime_episodes["aired"], errors = "coerce")
        return anime_episodes

    def get_reviews(self, preliminary: bool = True, spoilers: bool = True):
        reviews, reactions, users = super().get_reviews(preliminary = preliminary,
                                                        spoilers = spoilers)

        # https://myanimelist.net/reviews.php?id=505601
        reviews = reviews.rename(columns = {"mal_id": "id"})
        reviews["date"] = pd.to_datetime(reviews["date"], errors = "coerce")
        reviews = reviews[[
            "anime_id", "id", "type", "review", "score", "tags", "is_spoiler", "is_preliminary",
            "username", "date"
        ]]

        # reactions
        columns = [
            "anime_id", "id", "overall", "nice", "love_it", "funny", "confusing", "informative",
            "well_written", "creative"
        ]
        reactions = reactions.rename(columns = {"mal_id": "id"})[columns]

        return reviews, reactions, users

    def get_forum_messages(self, topic_id: int):
        forum_messages = super().get_forum_messages(topic_id)
        forum_messages = forum_messages.rename(columns = {"anime_id": "show_id"})
        columns = [
            "show_id", "forum_id", "id", "user", "datetime", "replied_id", "content",
            "additional_media"
        ]
        forum_messages = forum_messages[columns]
        return forum_messages


    # def get_statistics(self):
    #     statistics = self.get_parsed_json_from_api(f"/anime/{self.anime_id}/statistics")["data"]
    #     statistics_df = []
    #     for kpi_value in statistics:
    #         if kpi_value != "scores":
    #             statistics_df.append({
    #                 "kpi_name": "watching_status",
    #                 "kpi_value": kpi_value,
    #                 "amount": statistics[kpi_value]
    #             })
    #         else:
    #             for score in statistics[kpi_value]:
    #                 statistics_df.append({
    #                     "kpi_name": "score",
    #                     "kpi_value": f"score_{score['score']}",
    #                     "amount": score["votes"]
    #                 })
    #     statistics_df = pd.DataFrame(statistics_df)
    #     statistics_df["anime_id"] = self.anime_id
    #     return statistics_df

    # def _get_reviews_df(self, data):
    #     data_normalized = pd.json_normalize(data)

    #     # 1. Main Reviews
    #     reviews = pd.DataFrame(data).drop(columns=['reactions', 'user'])
    #     reviews["username"] = data_normalized['user.username']
    #     reviews["anime_id"] = self.anime_id

    #     # 2. Reactions (using mal_id as the foreign key)
    #     reaction_cols = [col for col in data_normalized if col.startswith('reactions.')]
    #     reactions = data_normalized[['mal_id'] + reaction_cols]
    #     reactions = reactions.rename(columns=lambda x: x.replace('reactions.', ''))
    #     reactions["anime_id"] = self.anime_id

    #     # 3. Users
    #     users = data_normalized[['user.username', 'user.url', 'user.images.jpg.image_url']]
    #     users = users.drop_duplicates(subset='user.username')
    #     return reviews, reactions, users

    # def get_reviews(self, preliminary: bool = True, spoilers: bool = True):
    #     query_params = f"?preliminary={str(preliminary).lower()}&spoilers={str(spoilers).lower()}"
    #     data = self.get_all_pages_from_endpoint(f"/anime/{self.anime_id}/reviews{query_params}")
    #     return self._get_reviews_df(data)

    # def get_user_updates(self):
    #     return self.get_all_pages_from_endpoint(f"/anime/{self.anime_id}/userupdates")

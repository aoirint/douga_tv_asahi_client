
from datetime import datetime, timedelta, timezone
from typing import List
import requests
import json
from pydantic import BaseModel

JST = timezone(timedelta(hours=9), 'JST')

class DougaTvAsahiEpisode(BaseModel):
  id: int
  index: int
  name: str
  description: str
  onair_at: datetime # date only


class DougaTvAsahiSeasonSeries(BaseModel):
  id: int
  name: str

class DougaTvAsahiSeason(BaseModel):
  id: int
  name: str
  series: DougaTvAsahiSeasonSeries
  episodes: List[DougaTvAsahiEpisode]


class DougaTvAsahiSeasonFetcher:
  def __init__(self, useragent: str):
    self.useragent = useragent

  # https://douga.tv-asahi.co.jp/program/{series_id}-{season_id}
  # ex) 相棒 season20: series_id=16839, season_id=29370
  def fetch_season_by_season_id(self, season_id: int) -> DougaTvAsahiSeason:
    url = 'https://douga.tv-asahi.co.jp/pathEvaluator'

    # [["meta","children","season_id"]]
    paths = json.dumps([['meta', 'children', str(season_id)]], separators=(',', ':'))

    params = {
      'paths': paths,
      'method': 'get',
    }

    res = requests.get(
      url,
      params=params,
      headers={
        'User-Agent': self.useragent,
      },
    )
    res.raise_for_status()

    data = res.json()
    json_graph = data['jsonGraph']
    meta = json_graph['meta']
    children = meta['children']
    child = children[str(season_id)]
    value = child['value'] # list of episodes

    first_episode = value[0]
    first_episode_values = first_episode['values']

    first_episode_parents_series = first_episode_values['parents_series']
    series_id = first_episode_parents_series['id']
    series_name = first_episode_parents_series['avails_SeriesTitleDisplayUnlimited']

    first_episode_parents_season = first_episode_values['parents_season']
    fetched_season_id = first_episode_parents_season['id']
    assert season_id == fetched_season_id # int == int
    season_name = first_episode_parents_season['avails_SeasonTitleDisplayUnlimited']

    episodes: List[DougaTvAsahiEpisode] = []

    for item in value:
      episode_id = item['id']
      episode_name = item['name']

      episode_values = item['values']
      episode_index = episode_values['avails_EpisodeNumber']
      episode_description = episode_values['evis_EpisodeLongSynopsis']
      episode_onair_at_jst_string = episode_values['avails_ReleaseHistoryOriginal'] # 2022/03/23 00:00:00
      episode_onair_at = datetime.strptime(episode_onair_at_jst_string, r'%Y/%m/%d %H:%M:%S').replace(tzinfo=JST) # 2022/03/23 00:00:00 +09:00

      episodes.append(
        DougaTvAsahiEpisode(
          id=episode_id,
          index=episode_index,
          name=episode_name,
          description=episode_description,
          onair_at=episode_onair_at,
        )
      )

    episodes.sort(key=lambda episode: episode.index)

    return DougaTvAsahiSeason(
      id=season_id,
      name=season_name,
      series=DougaTvAsahiSeasonSeries(
        id=series_id,
        name=series_name,
      ),
      episodes=episodes,
    )

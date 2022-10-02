import argparse
from io import StringIO
from pathlib import Path
import time
from typing import List
import csv

from tqdm import tqdm
from pydantic import BaseModel

from douga_tv_asahi.douga_tv_asahi_season import DougaTvAsahiSeasonFetcher


class Config:
  useragent: str = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36'

config = Config()


class SeasonIdListItem(BaseModel):
  order_index: int
  season_short_name: str
  season_id: int

def load_ordered_season_id_list() -> List[SeasonIdListItem]:
  season_id_list_csv_reader = csv.DictReader(StringIO(Path('data/season_id_list.csv').read_text(encoding='utf-8')))

  season_id_list_items: List[SeasonIdListItem] = []
  for row in season_id_list_csv_reader:
    season_id_list_items.append(
      SeasonIdListItem(
        order_index=int(row['order_index']),
        season_short_name= row['season_short_name'],
        season_id=int(row['season_id']),
      )
    )

  season_id_list_items.sort(key=lambda item: item.order_index)

  return season_id_list_items

def command_update_episodes(args):
  fetcher = DougaTvAsahiSeasonFetcher(useragent=config.useragent)
  ordered_season_id_list = load_ordered_season_id_list()

  with tqdm() as pbar:
    for season_id_item in ordered_season_id_list:
      episode_list_csv_path = Path('data/episode_list_by_season_short_name', f'{season_id_item.season_short_name}.csv')
      episode_list_csv_path.parent.mkdir(parents=True, exist_ok=True)

      pbar.set_postfix(
        {
          'season_short_name': season_id_item.season_short_name,
          'path': str(episode_list_csv_path),
        },
        refresh=True,
      )

      sio = StringIO()
      writer = csv.DictWriter(sio, fieldnames=['order_index','id','index','name','onair_at'])
      writer.writeheader()

      season = fetcher.fetch_season_by_season_id(season_id=season_id_item.season_id)
      for episode_order_index, episode in enumerate(season.episodes):
        writer.writerow({
          'order_index': episode_order_index,
          'id': episode.id,
          'index': episode.index,
          'name': episode.name,
          'onair_at': episode.onair_at.isoformat(),
        })

      episode_list_csv_path.write_text(sio.getvalue(), encoding='utf-8')
      time.sleep(0.1)


def main():
  parser = argparse.ArgumentParser()
  subparsers = parser.add_subparsers()
  parser_update_episodes = subparsers.add_parser('update_episodes')
  parser_update_episodes.set_defaults(handler=command_update_episodes)
  args = parser.parse_args()

  if hasattr(args, 'handler'):
    args.handler(args)
  else:
    parser.print_help()


if __name__ == '__main__':
  main()

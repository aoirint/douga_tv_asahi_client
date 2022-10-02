# douga_tv_asahi_client

## Usage

### Extract ID from URL

- Example URL: <https://douga.tv-asahi.co.jp/program/16839-29370>
  - series_id: `16839`
  - season_id: `29370`

### Create `data/season_id_list.csv`

#### Example

```csv
order_index,season_short_name,season_id
0,pre,24442
1,1,23499
2,2,24104
3,3,24126
4,4,24145
5,5,24167
6,6,24193
7,7,24213
8,8,23512
9,9,24233
10,10,24252
11,11,23532
12,12,24272
13,13,24292
14,14,23552
15,15,25150
16,16,25169
17,17,25190
18,18,24020
19,19,24668
20,20,29370
```

### Execute

```shell
python3 main.py update_episodes
```

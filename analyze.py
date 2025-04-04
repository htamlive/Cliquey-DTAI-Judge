import json
from pathlib import Path
import pandas as pd
import argparse
from tqdm import tqdm



TREASURE_VALUE_DIVISOR = 12

def parse_args():
    parser = argparse.ArgumentParser(description="Analyze bot match logs")
    parser.add_argument("--bot_matchs_json_dir_path", type=str, help="Path to the directory containing bot match logs in JSON format")
    parser.add_argument("--output_dir_path", type=str, help="Path to the output directory for the analysis results")
    return parser.parse_args()

def get_scores(round_log):
    players = round_log['players']
    return [player['points'] for player in players]

def check_current_coins_at_center(cells_state):
    for cell_state in cells_state:
        q, r, s = cell_state['q'], cell_state['r'], cell_state['s']
        if(q == r == s == 0):

            value = cell_state['value']
            if((isinstance(value, str) and value.isdigit()) or isinstance(value, int)):
                return int(value)
            
    return 0

def get_winners(final_round_log):
    players = final_round_log['players']

    points = [player['points'] for player in players]
    max_points = max(points)
    winners = [player_idx for player_idx, player in enumerate(players) if player['points'] == max_points]

    return winners


def get_who_got_treasure(bot_match_logs_json):
    init_round_log = bot_match_logs_json[0]
    last_round_log = init_round_log
    n_round = len(bot_match_logs_json)

    last_treasure_state = False
    

    for i in range(1, n_round):
        cur_round_log = bot_match_logs_json[i]
        last_scores = get_scores(last_round_log)
        cur_scores = get_scores(cur_round_log)

        map_state = last_round_log['map']
        cells_state = map_state['cells']
        players = cur_round_log['players']
        total_last_scores = sum(last_scores)

        cur_coins_at_center = check_current_coins_at_center(cells_state)

        pred_treasure_value = cur_coins_at_center + max(total_last_scores // TREASURE_VALUE_DIVISOR, 10)



        for player_idx, (player_cur_score, player_last_score) in enumerate(zip(cur_scores, last_scores)):
            player_log = players[player_idx]
            q, r, s = player_log['q'], player_log['r'], player_log['s']
            if player_cur_score - player_last_score >= pred_treasure_value and (q, r, s) == (0, 0, 0):
                return player_idx
            
        cur_treasure_state = map_state['treasure_remaining']
        if cur_treasure_state and not last_treasure_state:
            for player_idx, player_log in enumerate(players):
                q, r, s = player_log['q'], player_log['r'], player_log['s']
                if(q == r == s == 0):
                    return player_idx
                
        
        last_treasure_state = cur_treasure_state
        last_round_log = cur_round_log

    return None

def get_missile_accuracy(bot_match_logs_json):
    n_players = len(bot_match_logs_json[0]['players'])
    fired_missles = [0] * n_players
    hit_missles = [0] * n_players
    
    for player_idx in range(n_players):
        for round_log in bot_match_logs_json:
            other_locations = []
            for i in range(n_players):
                if i != player_idx:
                    other_locations.append((
                        round_log['players'][i]['q'],
                        round_log['players'][i]['r'],
                        round_log['players'][i]['s']
                    ))
            
            missiles_fired_locations = round_log['players'][player_idx]['missiles_fired']

            fired_missles[player_idx] += len(missiles_fired_locations)

            for fired_location in missiles_fired_locations:
                q, r, s = fired_location['q'], fired_location['r'], fired_location['s']
                if (q, r, s) in other_locations:
                    hit_missles[player_idx] += 1

    return hit_missles, fired_missles


def bot_match_analysis(bot_match_path: Path) -> pd.DataFrame:
    
    bot_match_logs_json = json.loads(bot_match_path.read_text(encoding='utf-8'))

    final_round_log = bot_match_logs_json[-1]


    final_scores = get_scores(final_round_log)
    winners = get_winners(final_round_log)

    who_got_treasure = get_who_got_treasure(bot_match_logs_json)
    hit_missles, fired_missles = get_missile_accuracy(bot_match_logs_json)

    winners_hot_encoded = [1 if i in winners else 0 for i in range(len(final_scores))]
    who_got_treasure_hot_encoded = [1 if i == who_got_treasure else 0 for i in range(len(final_scores))]

    df = pd.DataFrame({
        'player': ['bot1', 'bot2', 'bot3'],
        'final_score': final_scores,
        'winner': winners_hot_encoded,
        'who_got_treasure': who_got_treasure_hot_encoded,
        'missile_hit': hit_missles,
        'missile_fired': fired_missles
    })
    df['missile_accuracy'] = df['missile_hit'] / df['missile_fired']

    return df

if __name__ == "__main__":
    args = parse_args()
    bot_matchs_json_dir_path = Path(args.bot_matchs_json_dir_path)
    
    output_dir_path = Path(args.output_dir_path)
    output_dir_path.mkdir(parents=True, exist_ok=True)

    bot_matche_paths = list(bot_matchs_json_dir_path.glob('*.json'))

    for bot_match_path in tqdm(bot_matche_paths, desc="Analyzing bot match logs"):

        df = bot_match_analysis(bot_match_path)

        save_path = output_dir_path / f"{bot_match_path.stem}_analysis.csv"
        df.to_csv(save_path, index=False)
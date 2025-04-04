EX_AGENT_DIR=examples/agents
AGENT_DIR=../agents
MAP_DIR=examples/maps

MAP_NAME=map5
N_ROUNDS=10
MAX_WORKERS=20

AGENT_1_NAME=bot4
AGENT_1_FILE=$EX_AGENT_DIR/bot4/main.py
AGENT_2_NAME=phuc_old
AGENT_2_FILE=$AGENT_DIR/phuc_old/phuc_old.py
AGENT_3_NAME=Cliquey
AGENT_3_FILE=../out/Cliquey/main

MAP_PATH=$MAP_DIR/$MAP_NAME.json
MATCH_LOG_DIR=data/logs/$AGENT_1_NAME\_vs\_$AGENT_2_NAME\_vs\_$AGENT_3_NAME\_vs\_$MAP_NAME
ANALYZE_DIR=data/analyze_results/$AGENT_1_NAME\_vs\_$AGENT_2_NAME\_vs\_$AGENT_3_NAME\_vs\_$MAP_NAME

python run_benchmark.py \
    --agent1 $AGENT_1_FILE \
    --agent2 $AGENT_2_FILE \
    --agent3 $AGENT_3_FILE \
    --map_path $MAP_PATH \
    --n_rounds $N_ROUNDS \
    --max_workers $MAX_WORKERS && \
python analyze.py \
    --bot_matchs_json_dir_path $MATCH_LOG_DIR \
    --output_dir_path $ANALYZE_DIR && \
column -t -s, $ANALYZE_DIR/*.csv

# python analyze.py \
#     --bot_matchs_json_dir_path $MATCH_LOG_DIR \
#     --output_dir_path $ANALYZE_DIR

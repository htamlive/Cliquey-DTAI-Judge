MAP_DIR=examples/maps

MAP_NAME=$1
N_ROUNDS=$2
MAX_WORKERS=20

AGENT_1_FILE=$3
AGENT_2_FILE=$4
AGENT_3_FILE=$5

AGENT_1_NAME=$(basename $(dirname $AGENT_1_FILE))
AGENT_2_NAME=$(basename $(dirname $AGENT_2_FILE))
AGENT_3_NAME=$(basename $(dirname $AGENT_3_FILE))

echo "Running benchmark with agents: $AGENT_1_NAME (bot1), $AGENT_2_NAME (bot2), $AGENT_3_NAME (bot3) on map: $MAP_NAME"

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

python run_benchmark.py \
    --agent1 F:/Cliquey/Cliquey-DTAI-Judge/examples/agents/bot4/main.py \
    --agent2 F:/Cliquey/cliquey-ai/agents/phuc/phuc.py \
    --agent3 F:/Cliquey/cliquey-ai/out/vinh_agent/vinh_agent.exe \
    --map_path F:/Cliquey/cliquey-ai/Cliquey-DTAI-Judge/examples/maps/map15.json \
    --n_rounds 10 \
    --max_workers 10 && python analyze.py \
    --bot_matchs_json_dir_path data/logs/bot4_vs_phuc_vs_vinh_agent_vs_map15 \
    --output_dir_path data/analyze_results/bot4_vs_phuc_vs_vinh_agent_vs_map15 \
# Dau Truong AI 2025
Example command:
```bash
python main.py --map examples/maps/map.json --agents examples/agents/bot4/main.py examples/agents/bot5/main.py examples/agents/bot6/main.py --output data/logs/bot4_vs_bot5_vs_bot6.json
```

Before running the command, make sure the agent file is executable by running the following command:
```bash
chmod +x examples/agents/bot1/main.py
chmod +x examples/agents/bot2/main.py
chmod +x examples/agents/bot3/main.py
chmod +x examples/agents/bot4/main.py
chmod +x examples/agents/bot5/main.py
chmod +x examples/agents/bot6/main.py
chmod +x examples/agents/bot7/main.py
chmod +x examples/agents/bot8/main.py
chmod +x examples/agents/bot9/main.py
```

Currently, the runner is taking a agent as python file, could change to executable file by deleting the `python` in the `execute_agent` method in `runner.py` file.

https://dtai-visualizer.vercel.app/

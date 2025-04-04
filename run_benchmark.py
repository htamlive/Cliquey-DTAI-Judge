import subprocess
import os
from pathlib import Path
import json
import time
from tqdm import tqdm
import concurrent.futures
import argparse
import logging
import time
import tempfile
import shutil
import uuid
import random
import string
from typing import List

cur_time = time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime())

def generate_random_name(length=16):
    """Generate a strong random string to use as a folder name"""
    random_part = ''.join(random.choices(string.ascii_letters + string.digits, k=length))
    uuid_part = str(uuid.uuid4())
    return f"{random_part}_{uuid_part}"

def setup_logging(log_dir: Path):
    """Set up logging configuration"""
    log_file = log_dir / f"benchmark_{cur_time}.log"
    logging.basicConfig(
        filename=log_file,
        level=logging.INFO,
        format='%(asctime)s:%(levelname)s:%(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    logging.info("Logging setup complete.")

def parse_args():
    parser = argparse.ArgumentParser(description="Run benchmark for agents.")
    parser.add_argument("--agent1", type=str, required=True, help="Path to the first agent's executable. The parent folder name must be the bot name.")
    parser.add_argument("--agent2", type=str, required=True, help="Path to the second agent's executable. The parent folder name must be the bot name.")
    parser.add_argument("--agent3", type=str, required=True, help="Path to the third agent's executable. The parent folder name must be the bot name.")
    parser.add_argument("--n_rounds", type=int, default=10, help="Number of rounds to run")
    parser.add_argument("--current_round", type=int, default=0, help="Current round number (0-indexed)")
    parser.add_argument("--map_path", type=str, required=True, help="Path to the map JSON file")
    parser.add_argument("--log_dir", type=str, default="./data/logs/", help="Directory to save logs of matches")
    parser.add_argument("--benchmark_log_dir", type=str, default="./data/benchmark_logs", help="Directory to save benchmark logs")
    parser.add_argument("--max_workers", type=int, default=4, help="Maximum number of parallel processes")
    parser.add_argument("--work_dir", type=str, default=".", help="Base directory for creating temporary working directories")
    return parser.parse_args()

def run_single_round(round_idx, agent_paths: List[Path], map_path, match_log_dir, agent_names, work_dir):
    """Run a single round of the benchmark with private copies of agent files using strong random directory names"""

    map_name = Path(map_path).stem
    log_path: Path = match_log_dir / f"{agent_names[0]}_vs_{agent_names[1]}_vs_{agent_names[2]}_vs_{map_name}_round_{round_idx}.json"
    if log_path.exists():
        log_path = log_path.with_name(f"{log_path.stem}_copy{log_path.suffix}")
    
    random_dirname = generate_random_name()
    temp_dir = Path(work_dir) / f"round_{round_idx}_{random_dirname}"
    temp_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        agent_temp_dirs = []
        temp_agent_paths = []
        
        for i, agent_path in enumerate(agent_paths):
            agent_temp_dir = temp_dir / agent_path.parent.name
            agent_temp_dir.mkdir(parents=True, exist_ok=True)
            agent_temp_dirs.append(agent_temp_dir)
            
            agent_filename = agent_path.name
            temp_agent_path = agent_temp_dir / agent_filename
            shutil.copy2(agent_path, temp_agent_path)
            
            agent_dir = agent_path.parent
            for item in agent_dir.iterdir():
                if item.is_file() and item.absolute() != agent_path.absolute():
                    shutil.copy2(item, agent_temp_dir / item.name)
                elif item.is_dir():
                    shutil.copytree(item, agent_temp_dir / item.name, dirs_exist_ok=True)
            
            temp_agent_paths.append(temp_agent_path)
        
        abs_map_path = Path(map_path).absolute()
        abs_log_path = log_path.absolute()
        
        logging.debug(f"Round {round_idx} temp dir: {temp_dir}")
        for i, path in enumerate(temp_agent_paths):
            logging.debug(f"Round {round_idx} agent {i} path: {path}")
        
        process = subprocess.run(
            ["python", "main.py",
             "--map", str(abs_map_path),
             "--output", str(abs_log_path),
             "--agents", str(temp_agent_paths[0]), str(temp_agent_paths[1]), str(temp_agent_paths[2])
            ], 
            capture_output=True
        )
        
        return {
            "round_idx": round_idx,
            "log_path": str(log_path),
            "success": process.returncode == 0,
            "stdout": process.stdout.decode('utf-8'),
            "stderr": process.stderr.decode('utf-8'),
            "temp_dir": str(temp_dir)
        }
    except Exception as e:
        logging.error(f"Error in round {round_idx}: {str(e)}")
        shutil.rmtree(temp_dir, ignore_errors=True)
        raise
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)

if __name__ == "__main__":
    args = parse_args()

    agent_paths = [Path(args.agent1), Path(args.agent2), Path(args.agent3)]
    n_rounds = args.n_rounds
    current_round = args.current_round
    map_path = args.map_path
    max_workers = args.max_workers
    work_dir = args.work_dir

    agent_names = [path.parent.name for path in agent_paths]
    map_name = Path(map_path).stem
    match_name = f"{agent_names[0]}_vs_{agent_names[1]}_vs_{agent_names[2]}_vs_{map_name}"

    log_dir = args.log_dir
    os.makedirs(log_dir, exist_ok=True)

    match_log_dir = Path(log_dir) / match_name
    os.makedirs(match_log_dir, exist_ok=True)

    benchmark_log_dir = Path(args.benchmark_log_dir) / match_name
    os.makedirs(benchmark_log_dir, exist_ok=True)

    base_work_dir = Path(work_dir) / "playground"
    os.makedirs(base_work_dir, exist_ok=True)

    benchmark_file = benchmark_log_dir / f"benchmark_{cur_time}.log"
    setup_logging(benchmark_log_dir)

    logger = logging.getLogger("Benchmark")

    rounds_to_run = list(range(current_round, n_rounds))
    total_rounds = len(rounds_to_run)
    
    progress_bar = tqdm(total=total_rounds, desc="Running benchmark rounds")
    
    successful_rounds = []
    failed_rounds = []
    temp_dirs = [] 

    with concurrent.futures.ProcessPoolExecutor(max_workers=max_workers) as executor:
        future_to_round = {
            executor.submit(run_single_round, round_idx, agent_paths, map_path, match_log_dir, agent_names, base_work_dir): round_idx
            for round_idx in rounds_to_run
        }
        
        for future in concurrent.futures.as_completed(future_to_round):
            round_idx = future_to_round[future]
            try:
                result = future.result()
                if result["success"]:
                    successful_rounds.append(round_idx)
                    logger.info(f"Round {round_idx + 1}/{n_rounds} completed. Log saved to {result['log_path']}.")
                else:
                    failed_rounds.append(round_idx)
                    logger.error(f"Round {round_idx + 1}/{n_rounds} failed. Error: {result['stderr']}")
                
                if "temp_dir" in result:
                    temp_dirs.append(result["temp_dir"])
                    
            except Exception as e:
                failed_rounds.append(round_idx)
                logger.error(f"Round {round_idx + 1}/{n_rounds} raised an exception: {e}")
            
            progress_bar.update(1)
    
    progress_bar.close()
    
    for temp_dir in temp_dirs:
        try:
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir, ignore_errors=True)
        except Exception as e:
            logger.warning(f"Failed to clean up temporary directory {temp_dir}: {e}")
    
    try:
        shutil.rmtree(base_work_dir, ignore_errors=True)
    except OSError as e:
        logger.warning(f"Could not remove base working directory {base_work_dir}: {e}")
    
    print(f"\nBenchmark complete: {len(successful_rounds)}/{total_rounds} rounds successful.")
    logger.info(f"Benchmark complete: {len(successful_rounds)}/{total_rounds} rounds successful.")
    if failed_rounds:
        print(f"Failed rounds: {', '.join(map(str, failed_rounds))}")
        logger.info(f"Failed rounds: {', '.join(map(str, failed_rounds))}")
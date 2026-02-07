#!/usr/bin/env python3
"""
🔧 CloudBrain AI Agent Daemon Manager

Run autonomous AI agents as daemon/service with automatic restart.
"""

import os
import sys
import signal
import time
import subprocess
import argparse
from pathlib import Path
from datetime import datetime

class AIAgentDaemon:
    """Manage AI agent as daemon/service"""
    
    def __init__(self, ai_name: str, script_path: str = None):
        self.ai_name = ai_name
        self.script_path = script_path or str(Path(__file__).parent / "autonomous_ai_agent.py")
        self.pid_file = f"/tmp/cloudbrain_agent_{ai_name}.pid"
        self.log_file = f"/tmp/cloudbrain_agent_{ai_name}.log"
        self.process = None
        self.running = False
        
        signal.signal(signal.SIGINT, self.handle_shutdown)
        signal.signal(signal.SIGTERM, self.handle_shutdown)
    
    def is_running(self) -> bool:
        """Check if daemon is already running"""
        if not os.path.exists(self.pid_file):
            return False
        
        try:
            with open(self.pid_file, 'r') as f:
                pid = int(f.read().strip())
            
            os.kill(pid, 0)
            return True
        except (OSError, ValueError):
            return False
    
    def start(self, server_url: str = "ws://127.0.0.1:8768"):
        """Start daemon"""
        if self.is_running():
            print(f"❌ Daemon for {self.ai_name} is already running")
            print(f"   PID file: {self.pid_file}")
            return False
        
        print(f"🚀 Starting daemon for {self.ai_name}...")
        print(f"   Script: {self.script_path}")
        print(f"   Server: {server_url}")
        print(f"   Log: {self.log_file}")
        
        # Start process
        try:
            with open(self.log_file, 'a') as log:
                log.write(f"\n{'=' * 70}\n")
                log.write(f"🚀 Daemon started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                log.write(f"   AI: {self.ai_name}\n")
                log.write(f"   Server: {server_url}\n")
                log.write(f"{'=' * 70}\n\n")
                log.flush()
            
            self.process = subprocess.Popen(
                [sys.executable, self.script_path, self.ai_name, "--server", server_url],
                stdout=open(self.log_file, 'a'),
                stderr=subprocess.STDOUT,
                start_new_session=True
            )
            
            # Write PID
            with open(self.pid_file, 'w') as f:
                f.write(str(self.process.pid))
            
            self.running = True
            print(f"✅ Daemon started for {self.ai_name}")
            print(f"   PID: {self.process.pid}")
            print(f"   Log: {self.log_file}")
            print(f"   PID file: {self.pid_file}")
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to start daemon: {e}")
            return False
    
    def stop(self):
        """Stop daemon"""
        if not self.is_running():
            print(f"⚠️  Daemon for {self.ai_name} is not running")
            return False
        
        print(f"🛑 Stopping daemon for {self.ai_name}...")
        
        try:
            with open(self.pid_file, 'r') as f:
                pid = int(f.read().strip())
            
            os.kill(pid, signal.SIGTERM)
            
            # Wait for process to stop
            for _ in range(10):
                try:
                    os.kill(pid, 0)
                    time.sleep(0.5)
                except OSError:
                    break
            
            # Force kill if still running
            try:
                os.kill(pid, 0)
                os.kill(pid, signal.SIGKILL)
            except OSError:
                pass
            
            os.remove(self.pid_file)
            print(f"✅ Daemon stopped for {self.ai_name}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to stop daemon: {e}")
            return False
    
    def restart(self, server_url: str = "ws://127.0.0.1:8768"):
        """Restart daemon"""
        print(f"🔄 Restarting daemon for {self.ai_name}...")
        self.stop()
        time.sleep(2)
        return self.start(server_url)
    
    def status(self):
        """Check daemon status"""
        if not self.is_running():
            print(f"⚠️  Daemon for {self.ai_name} is NOT running")
            return False
        
        try:
            with open(self.pid_file, 'r') as f:
                pid = int(f.read().strip())
            
            print(f"✅ Daemon for {self.ai_name} is running")
            print(f"   PID: {pid}")
            print(f"   Log: {self.log_file}")
            
            # Check process details
            try:
                import psutil
                proc = psutil.Process(pid)
                print(f"   CPU: {proc.cpu_percent()}%")
                print(f"   Memory: {proc.memory_info().rss / 1024 / 1024:.1f} MB")
                print(f"   Threads: {proc.num_threads()}")
            except ImportError:
                pass
            
            return True
            
        except Exception as e:
            print(f"❌ Error checking status: {e}")
            return False
    
    def logs(self, lines: int = 50):
        """Show daemon logs"""
        if not os.path.exists(self.log_file):
            print(f"❌ Log file not found: {self.log_file}")
            return
        
        print(f"📜 Last {lines} lines from {self.log_file}:")
        print("=" * 70)
        
        try:
            with open(self.log_file, 'r') as f:
                log_lines = f.readlines()
            
            for line in log_lines[-lines:]:
                print(line.rstrip())
                
        except Exception as e:
            print(f"❌ Error reading logs: {e}")
    
    def handle_shutdown(self, signum, frame):
        """Handle shutdown signals"""
        print(f"\n🛑 Received signal {signum}, shutting down...")
        if self.running:
            self.stop()
        sys.exit(0)


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="CloudBrain AI Agent Daemon Manager",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument("ai_name", help="AI agent name")
    parser.add_argument("command", choices=['start', 'stop', 'restart', 'status', 'logs'], help="Command to execute")
    parser.add_argument("--server", default="ws://127.0.0.1:8768", help="CloudBrain server URL")
    parser.add_argument("--script", help="Path to autonomous_ai_agent.py script")
    parser.add_argument("--lines", type=int, default=50, help="Number of log lines to show")
    
    args = parser.parse_args()
    
    daemon = AIAgentDaemon(args.ai_name, args.script)
    
    if args.command == 'start':
        daemon.start(args.server)
    elif args.command == 'stop':
        daemon.stop()
    elif args.command == 'restart':
        daemon.restart(args.server)
    elif args.command == 'status':
        daemon.status()
    elif args.command == 'logs':
        daemon.logs(args.lines)


if __name__ == "__main__":
    main()

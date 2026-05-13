import subprocess
import time

process = subprocess.Popen(["ollama", "serve"])

time.sleep(5)

print("Ollama server started")
subprocess.Popen(['ollama', 'pull', 'phi3'])
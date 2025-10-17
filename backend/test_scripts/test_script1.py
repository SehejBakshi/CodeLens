import os
import subprocess

class FileHandler:
    def __init__(self, filename):
        self.filename = filename

    def read_file(self):
        with open(self.filename, 'r') as f:
            data = f.read()
        return data

def run_command(cmd):
    # SECURITY ISSUE: Direct shell command execution
    subprocess.call(cmd, shell=True)

def main():
    handler = FileHandler("test.txt")
    content = handler.read_file()
    run_command(f"echo {content}")

if __name__ == "__main__":
    main()

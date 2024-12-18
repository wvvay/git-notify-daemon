import subprocess

ls_lines = subprocess.run(['ls', '-l'], stdout=subprocess.PIPE).stdout
print(ls_line)
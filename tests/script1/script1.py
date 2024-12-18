import subprocess

output = subbprocess.run(['pwd'], capture_output=True, text=True)
output = output.stdout

print(f'Your current directory: {output}')



arrlines2 = []
with open("example.txt", "r") as file:
    for line in file:
        arrlines.append(line)
        print(line)

with open("output.txt", "w+") as f:
    for  line in arrlines:
        f.write(str(line) + '\n')
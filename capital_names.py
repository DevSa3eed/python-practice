Name = ""
Capital_name_list = []
while (Name != "fin"):
    Name = input("Name?")
    if Name.istitle():
        Capital_name_list.append(Name)
print(str(len(Capital_name_list)) + ' names start with capital letters')

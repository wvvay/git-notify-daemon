from sys import platform
if platform == "Ubuntu18.04" or platform == "Ubuntu22.04":
    print('Вы рабоотаете на linux')
    pass
elif platform == "macOS":
    print('Вы работаете на MacOS')
    pass
elif platform == "win":
    print('Вы работаете на Windows')
    pass
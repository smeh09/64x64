import random

map_1 = '''
xxxxxxxxxxxxxxxxxxxx
xxxxxxxxxxxxxxxxxxxx
xxxxxxxxxxxxxxxxxxxx
xxxxxxxxxxxxxxxxxxxx
xxxxxxxxxxxxxxxxxxxx
xxxxxxxxxxxxxxxxxxxx
xxxxxxxxxxxxx513xxxx
xxxx5113xxxx57463xxx
11117446111174446111
44444444444444444444
44444444444444444444
44444444444444444444
'''

map_2 = '''
xxxxxxxxxxxxxxxxxxxx
xxxxxxxxxxxxxxxxxxxx
xxxxxxxxxxxxxxxxxxxx
xxxxxxxxxxxxxxxxxxxx
xxxxxxxxxxxxxxxxxxxx
xxxxxxxxxxxxxxxxxxxx
xxxxxxxxxxxxxxxxxxxx
xxxxxxxxxxxxxxxxxxxx
11111111111111111111
44444444444444444444
44444444444444444444
44444444444444444444
'''

map_3 = '''
xxxxxxxxxxxxxxxxxxxx
xxxxxxxxxxxxxxxxxxxx
xxxxxxxxxxxxxxxxxxxx
xxxxxxxxxxxxxxxxxxxx
xxxxxxxxxxxxxxxxxxxx
xxxxxxxxxxxxxxxxxxxx
xxxxxxx511113xxxxxxx
xxxxxx57444463xxxxxx
11111174444446111111
44444444444444444444
44444444444444444444
44444444444444444444
'''

map_3 = '''
xxxxxxxxxxxxxxxxxxxx
xxxxxxxxxxxxxxxxxxxx
xxxxxxxxxxxxxxxxxxxx
xxxxxxxxxxxxxxxxxxxx
xxxxxxxxxxxxxxxxxxxx
xxxxxxxxxxxxxxxxxxxx
xxxxxxxx5113xxxxxxxx
xxxxxx51744613xxxxxx
11111174444446111111
44444444444444444444
44444444444444444444
44444444444444444444
'''

map_4 = '''
xxxxxxxxxxxxxxxxxxxx
xxxxxxxxxxxxxxxxxxxx
xxxxxxxxxxxxxxxxxxxx
xxxxxxxxxxxxxxxxxxxx
xxxxxxxxxxxxxxxxxxxx
xxxxxxxxxxxxxxxxxxxx
xxxxxxxxxxxxxxxxxxxx
xxxxxxxxxxxxxxxxxxxx
11113xxxxxxxxxx51111
44446xxxxxxxxxx74444
44444xxxxxxxxxx44444
44444xxxxxxxxxx44444
'''

map_5 = '''
xxxxxxxxxxxxxxxxxxxx
xxxxxxxxxxxxxxxxxxxx
xxxxxxxxxxxxxxxxxxxx
xxxxxxxxxxxxxxxxxxxx
xxxxxxxxxxxxxxxxxxxx
xxxxxxxxxxxxxxxxxxxx
xxxxxxxxxxxxxxxxxxxx
xxxxxxxxxxxxxxxxxxxx
xxxxxx11111111xxxxxx
xxxxxx44444444xxxxxx
xxxxxx44444444xxxxxx
xxxxxx44444444xxxxxx
'''

map_6 = '''
xxxxxxxxxxxxxxxxxxxx
xxxxxxxxxxxxxxxxxxxx
xxxxxxxxxxxxxxxxxxxx
xxxxxxxxxxxxxxxxxxxx
xxxxxxxxxxxxxxxxxxxx
xxxxxxxxxxxxxxxxxxxx
3xxxxxxxxxxxxxxxxxx5
63xxxxxxxxxxxxxxxx57
46111111111111111174
44444444444444444444
44444444444444444444
44444444444444444444
'''

i = random.randint(0, 5)
selected_map = {'maps': [map_1, map_2, map_3, map_4, map_5, map_6], 'index': i}
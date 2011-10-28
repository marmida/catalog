'''
mock implementations

'''
import random

def list_tags():
    return [
        'Absinthe dreams',
        'Abstract Westerns',
        'Aliens',
        'Alter egos',
        'Altered states',
        'Alternative',
        'Badminton',
        'Barf',
        'Bourgeoisie',
        'Budget',
        'Bullshit',
        'Captialism',
        'Communism',
        'Construction',
        'Electrical currents',
        'Fables',
        'Furious Cats',
        'Gold rush',
        'Hammers &amp; Hamsters',
        'Librarian Propaganda',
        'Marmoset documentaries',
        'Mango production worldwide',
        'Netherlands',
        'Populism',
        'Pretentious bullshit',
        'Strychnine',
        'Tow trucks',
        'Underwater public transportation',
        'Wilted vegetables',
        'Xylophones',
        'Zoological explosions',
    ]

def match_search():
    ret = [
        {
            'filename': 'hello_kitty.flv',
            'path': '/home/marmida/Movies/hello_kitty.flv',
        },
        {
            'filename': 'Garfunkel and Oates.flv',
            'path': '/home/marmida/Movies/Garfunkel and Oates.flv',
        },
    ]
    
    # return a blank result on one out of three clicks
    return ret if random.randint(0,4) != 3 else []
    
def file_info():
    return {
        'filename': 'hello_kitty.flv',
        'path': '/home/marmida/Videos/kawaii',
    }

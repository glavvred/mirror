from transitions import Machine


class Menu(object):
    pass


position = Menu()

states = ['main', 'face_recognition',
          'hello', 'hello_stranger',
          'await',
          'bye', 'chat', 'filthy', 'news', 'depression', 'thanks', 'help', 'bored', 'question',
          'failure']  # 'weather', 'traffic'

transitions = [
    {'trigger': 'wake', 'source': 'main', 'dest': 'face_recognition'},
    {'trigger': 'sleep', 'source': 'face_recognition', 'dest': 'main'},
    {'trigger': 'found_face', 'source': 'face_recognition', 'dest': 'hello'},
    {'trigger': 'i_know_you', 'source': 'face_recognition', 'dest': 'hello_stranger'},
    {'trigger': 'ionize', 'source': 'gas', 'dest': 'plasma'}
]

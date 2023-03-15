from transitions import Machine


class Mirror(object):
    states = ['asleep', 'movement found',
              'hello user', 'hello stranger',
              'await',
              'bye', 'chat', 'filthy', 'news', 'depression', 'thanks', 'help', 'bored', 'question',
              'failure']  # 'weather', 'traffic'

    transitions = [
        {'trigger': 'found_face', 'source': 'face recognition', 'dest': 'hello'},
        {'trigger': 'i_know_you', 'source': 'face recognition', 'dest': 'hello stranger'},

    ]

    def __init__(self, name):
        self.name = name
        self.motion_detected = False
        self.machine = Machine(model=self, states=Mirror.states, initial='asleep')

        # At some point, every superhero must rise and shine.
        self.machine.add_transition(trigger='go_sleep', source='*', dest='asleep')
        self.machine.add_transition(trigger='wake_up', source='asleep', dest='movement found')
        self.machine.add_transition(trigger='found_face', source='movement found', dest='hello stranger')
        self.machine.add_transition(trigger='found_known_face', source=['movement found', 'hello stranger'],
                                    dest='hello user')


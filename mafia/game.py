from enum import Enum
import random

import protos.engine_pb2 as engine_pb2

class State(Enum):
    PENDING = 1
    STARTED = 2
    ENDED = 3

class Game:
    def __init__(self, id, max_players = 4):
        self.max_players = max_players
        self.id = id
        self.is_full = False
        self.status = State.PENDING
        self.actions = 0

        self.roles = dict()
        self.players = []
        self.dead_players = []
        self.ready_to_start = []
        self.mafias = []

        self.votes = dict()
        # self.vote_name = ''

        self.is_publish = False
        self.checks = dict()
    
        self.end = []
        self.end_cond = []

    # utils

    def append_mafia(self, name):
        self.mafias.append(name)
    
    def set_night(self):
        self.votes = dict()
        self.time = 'night'

    def set_day(self):
        self.votes = dict()
        self.time = 'day'
    
    def set_end(self):
        self.votes = dict()
        self.status = State.ENDED

    def inc_start(self, name) -> str:
        if name in self.ready_to_start:
            return 'The request has already been sent'
        self.ready_to_start.append(name)
        
        if len(self.ready_to_start) == self.max_players:
            self.ready_to_start = []
            self.status = State.STARTED
            return 'start'
        return 'wait'
    
    def inc_end(self, name) -> str:
        if name in self.end:
            return 'The request has already been sent'
        self.end.append(name)
        if len(self.end) == self.max_players - len(self.dead_players):
            self.end = []
            return 'start'
        return 'wait'

    def append_player(self, name) -> bool:
        if self.is_full:
            return False
        self.players.append(name)
        if len(self.players) == self.max_players:
            self.is_full = True
        return True
    
    def append_dead_player(self, name):
        self.dead_players.append(name)
    
    # game
    def set_roles(self):
        self.roles_names = ['Sheriff']
        for i in range(self.max_players // 3):
            self.roles_names.append('Mafia')
        for i in range(self.max_players - len(self.roles)):
            self.roles_names.append('Villager')

        random.shuffle(self.roles_names)
        for i in range(len(self.players)):
            self.roles[self.players[i]] = self.roles_names[i]
            if self.roles_names[i] == 'Mafia':
                self.append_mafia(self.players[i])
    
    def leave(self, name):
        if name not in self.players:
            return
        self.players.remove(name)
        if name in self.dead_players:
            self.dead_players.remove(name)
        else:
            print('leave')
            exit()
    
    def publish(self, request):
        if request.name in self.dead_players:
            return 'You are ghost!'
        return str(self.checks)
    

    # DAY ACTIONS
    def vote(self, request: engine_pb2.VoteRequest) -> None:
        if request.name in self.dead_players:
            return 'You are ghost!'
        
        if request.vote_name in self.dead_players:
            return request.vote_name + 'is already dead! Dead players:' + ' '.join(self.dead_players)

        if request.vote_name not in self.players:
            return 'You entered the wrong name! Choose from: %s' % ' '.join(self.players)
        
        if request.name == request.vote_name:
            return 'You can not vote yourself!'

        if request.vote_name in self.votes.keys():
            self.votes[request.vote_name] += 1
        else:
            self.votes[request.vote_name] = 1
        self.actions += 1
        return 'success'

    # NIGHT ACTIONS
    def kill(self, request: engine_pb2.KillRequest) -> str: 
        if request.name in self.dead_players:
            return 'You are ghost!'
    
        if self.roles[request.name] != 'Mafia':
            return 'You are not mafia!'
        
        if request.kill_name in self.dead_players:
            return request.kill_name + 'is already dead! Dead players:' + ' '.join(self.dead_players)

        if request.kill_name not in self.players:
            return 'You entered the wrong name! Choose from: %s' % ' '.join(self.players)
        
        if request.name == request.kill_name:
            return 'You can not kill yourself!'
        
        if request.kill_name in self.mafias:
            return 'You can not kill another mafia! Mafias: %s' % ' '.join(self.mafias)

        if request.kill_name in self.votes.keys():
            self.votes[request.kill_name] += 1
        else:
            self.votes[request.kill_name] = 1
        self.actions += 1
        return 'success'
    
    def check(self, request: engine_pb2.CheckRequest) -> str: 
        if request.name in self.dead_players:
            return 'You are ghost!'
    
        if self.roles[request.name] != 'Sheriff':
            return 'You are not Sheriff!'

        if request.check_name in self.dead_players:
            return request.check_name + 'is already dead! Dead players:' + ' '.join(self.dead_players)

        if request.check_name not in self.players:
            return 'You entered the wrong name! Choose from: %s' % ' '.join(self.players)
        
        if request.name == request.check_name:
            return 'You can not check yourself!'

        self.checks[request.check_name] = self.roles[request.check_name]
        return self.roles[request.check_name]
    
    # DAY OR NIGHT RESULTS
    def vote_or_kill_result(self) -> str:
        max_name = ''
        max_count = 0
        for name, count in self.votes.items():
            if max_count < count:
                max_name = name
                max_count = count

        for name, count in self.votes.items():
            if max_name != name and max_count == count:
                self.votes = dict()
                return ''
        return max_name

    def check_game_end(self) -> tuple:
        alive_mafias = 0
        alive_villagers = 0
        for name in self.players:
            if name in self.dead_players:
                continue
            if self.roles[name] == 'Mafia':
                alive_mafias += 1
            else:
                alive_villagers += 1
        return alive_mafias, alive_villagers

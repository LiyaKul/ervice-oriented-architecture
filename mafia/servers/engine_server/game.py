from enum import Enum
import logging
import asyncio
import random

import mafia.protos.engine_pb2 as engine_pb2

from game_state import *

class State(Enum):
    PENDING = 1
    STARTED = 2
    ENDED = 3

class Game:
    def __init__(self, id, max_players = 4):
        self.votes = dict()
        self.vote_name = ''
        self.roles = dict()

        self.is_publish = False
        self.checks = str()
    
        self.id = id
        self.state = GameState(id, max_players)
        self.players = []
        self.dead_players = []
        self.end = []
        self.ready_to_start = []
        self.end_cond = []
        self.actions = 0
        self.is_full = False
        self.mafias = []
    
    # GAME STATE
    def count(self):
        return self.state.max_players
    
    # def id(self):
    #     return self.state.id
    
    def append_mafia(self, name):
        self.state.mafias.append(name)

    def status(self):
        return self.state.status
    
    def time(self):
        return self.state.time

    def set_night(self):
        self.state.time = 'night'

    def set_day(self):
        self.state.time = 'day'
    
    def set_end(self):
        self.state.status = State.ENDED

    # utils
    def inc_start(self, name) -> str:
        if name in self.ready_to_start:
            return 'The request has already been sent'
        self.ready_to_start.append(name)
        
        if len(self.ready_to_start) == self.count():
            self.ready_to_start = []
            return 'start'
        return 'wait'
    
    def inc_end(self, name) -> str:
        if name in self.end:
            return 'The request has already been sent'
        self.end.append(name)
        if len(self.end) == self.count():
            self.end = []
            return 'start'
        return 'wait'

    def append_player(self, name) -> bool:
        if self.is_full:
            return False
        self.players.append(name)
        if len(self.players) == self.count():
            self.is_full = True
        return True
    
    def append_dead_player(self, name):
        self.dead_players.append(name)
    
    def set_roles(self):
        self.roles_names = []
        for i in range(self.count() // 3):
            self.roles_names.append('Mafia')
        self.roles_names.append('Sheriff')
        for i in range(self.state.max_players - len(self.roles)):
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
        return self.checks
    

    # DAY ACTIONS
    def vote(self, request: engine_pb2.VoteRequest) -> None:
        if request.name in self.dead_players:
            return 'You are ghost!'
    
        if self.time() != 'day':
            return 'You can not vote now!'
        
        if request.vote_name in self.dead_players:
            return '%s is already dead! Dead players: %s' % ' '.join(self.dead_players)

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

        if self.time() != 'night':
            return 'You can not kill now!'
        
        if request.kill_name in self.dead_players:
            return '%s is already dead! Dead players: %s' % ' '.join(self.dead_players)

        if request.kill_name not in self.players:
            return 'You entered the wrong name! Choose from: %s' % ' '.join(self.players)
        
        if request.name == request.kill_name:
            return 'You can not kill yourself!'
        
        if request.kill_name in self.state.mafias:
            return 'You can not kill another mafia! Mafias: %s' % ' '.join(self.state.mafias)

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

        if self.time() != 'night':
            return 'You can not check now!'
        
        if request.check_name in self.dead_players:
            return '%s is already dead! Dead players: %s' % ' '.join(self.dead_players)

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
                print(self.votes, max_name)
                return ''
        return max_name




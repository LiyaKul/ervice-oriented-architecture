from enum import Enum
import logging
import asyncio
import random

import mafia.protos.engine_pb2 as engine_pb2

class State(Enum):
    PENDING = 1
    STARTED = 2
    ENDED = 3

class Game:
    def __init__(self, id, max_players = 4):
        self.id = id
        self.max_players = max_players
        self.players = dict()
        self.is_full = False
        self.status = State.PENDING
        self.current_message = ''
        self.roles_indexes = ['Sheriff', 'Mafia', 'Villager', 'Villager']
        self.mafias = []
        self.actions_count = 0
        self.dead_players = []
        self.type = 'day'
        self.action_cond = asyncio.Condition()
        self.votes = dict()
        self.first_player = ''
        self.vote_name = ''
        self.game_count = 0
        self.log_name = ''
        self.roles = dict()
        self.is_publish = False
        self.checks = str()
        self.notify_cond = asyncio.Condition()


    def get_status(self):
        return self.status
    
    def append_player(self, name, id) -> bool:
        if self.is_full:
            return False
        self.players[name] = id
        if len(self.players) == self.max_players:
            self.is_full = True
        return True
    
    def set_roles_indexes(self):
        random.shuffle(self.roles_indexes)
        for i in range(len(self.roles_indexes)):
            if self.roles_indexes[i] == 'Mafia':
                self.mafias.append(str(i+1))
        for name, id in self.players.items():
            self.roles[name] = self.roles_indexes[id - 1]
    
    def handle_vote(self, request: engine_pb2.ActionRequest) -> None:
        if request.vote_name != '':   
            if request.vote_name in self.dead_players:
                return
            if request.vote_name in self.votes.keys():
                self.votes[request.vote_name] += 1
            else:
                self.votes[request.vote_name] = 1
        elif request.action_name != '':
            if self.type == 'night' and self.roles_indexes[self.players[request.name]-1] != 'Mafia':
                return
            if request.action_name in self.votes.keys():
                self.votes[request.action_name] += 1
            else:
                self.votes[request.action_name] = 1
    
    def vote_result(self) -> str:
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
        print(self.votes, max_name)
        return max_name


    def check_game_end(self) -> tuple:
        alive_mafias = 0
        alive_villagers = 0
        for name in self.players.keys():
            if name in self.dead_players:
                continue
            if self.role[name] == 'Mafia':
                alive_mafias += 1
            else:
                alive_villagers += 1
        return alive_mafias, alive_villagers

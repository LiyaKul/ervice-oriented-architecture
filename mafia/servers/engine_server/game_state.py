from enum import Enum
import logging
import asyncio
import random

import mafia.protos.engine_pb2 as engine_pb2

class State(Enum):
    PENDING = 1
    STARTED = 2
    ENDED = 3

class GameState:
    def __init__(self, id, max_players = 4):
        self.id = id
        self.max_players = max_players
        self.players = []
        self.start_count = 0
        self.is_full = False
        self.status = State.PENDING
        self.mafias = []
        self.dead_players = []
        self.type = 'night'
        self.day_count = 0
    
    def append_player(self, name) -> bool:
        if self.is_full:
            return False
        self.players.append(name)
        if len(self.players) == self.max_players:
            self.is_full = True
        return True
    
    def append_dead_player(self, name):
        self.dead_players.append(name)
    
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
    


import grpc
import logging
import asyncio
import random
import string
from enum import Enum

import sys
sys.path.append('../../')
sys.path.append('../../../')
sys.path.append('..')
sys.path.append('.')
import mafia.protos.engine_pb2 as engine_pb2
import mafia.protos.engine_pb2_grpc as engine_pb2_grpc

from roles import *
class MessageType(Enum):
    INFO = 1
    DEATH = 2
    PUBLISH = 3
    END = 4

class RandomPlayer:
    def __init__(self, stub: engine_pb2_grpc.EngineServerStub):
        self.stub = stub
        self.name = ''.join(random.choice(string.ascii_uppercase) for _ in range(7)) # https://stackoverflow.com/questions/2030053/how-to-generate-random-strings-in-python
        self.request_type = 'day'
        self.action_cond = asyncio.Condition()
        self.checks = dict()
        self.check_name = None
        self.time = 'day'
        self.game_end = False
        self.is_alive = True

    async def join(self) -> None:
        response = await self.stub.Join(engine_pb2.JoinRequest(name=self.name, text='hello'))
        logging.info(self.name + ': ' + response.text)
        self.id = response.id
        return response.id != -1

    async def get_players(self) -> None:
        response = await self.stub.GetPlayers(engine_pb2.GetPlayersRequest(name=self.name, text='hello'))
        self.players = response.names.split('%')
        logging.info(self.name + ': Received players:' + response.names.replace('%', ', '))

    async def want_to_start(self):
        response = await self.stub.Start(engine_pb2.StartRequest(name=self.name, text='hello'))
        if not response.started:
            logging.info(self.name + ': Im not in game :(')
            return False
        logging.info(self.name + ': I got the %s role!' % response.role)
        self.players = response.players.split('%')
        if response.role == 'Sheriff':
            self.role = Sheriff(self.id, self.players, self.name)
        elif response.role == 'Mafia':
            self.role = Mafia(self.id, self.players, self.name, list(response.mafias.split('%')))
        else:
            self.role = Villager(self.id, self.players, self.name)
        return response.started
    
    async def kill(self):
        if self.role.role == 'Mafia':
            response = await self.stub.Kill(engine_pb2.KillRequest(name=self.name, kill_name=self.role.action()))

    async def check(self):
        if self.role.role == 'Sheriff':
            response = await self.stub.Check(engine_pb2.CheckRequest(name=self.name, check_name=self.role.action()))

    async def vote(self):
        await self.stub.Vote(engine_pb2.VoteRequest(name=self.name, vote_name=self.role.vote()))
    
    async def end_day(self):
        response = await self.stub.EndDay(engine_pb2.EndDayRequest(name=self.name))
        if response.ended:
            self.time = 'night'

    
    async def end_night(self):
        response = await self.stub.EndNight(engine_pb2.EndNightRequest(name=self.name))
        if response.ended:
            self.time = 'day'
    
    async def start_game(self):
        if not await self.want_to_start():
            exit()
        await self.get_players()
        for i in range(10):
            if not self.is_alive or self.game_end:
                break
            if self.time == 'night':
                if self.role.role == 'Sheriff':
                    await self.check()
                    await asyncio.sleep(0.5)
                elif self.role.role == 'Mafia':
                    await self.kill()
                    await asyncio.sleep(0.5)
                await self.end_night()
                await asyncio.sleep(0.5)
                self.time = 'day'
            elif self.time == 'day':
                await self.vote()
                await asyncio.sleep(0.5)
                await self.end_day()
                await asyncio.sleep(0.5)
                await asyncio.sleep(0.5)
                self.time = 'night'


    async def get_messages(self):
        messages = self.stub.GameInfo(engine_pb2.InfoRequest(name=self.name, text='hello'))
        async for message in messages:
            logging.info(self.name + ': "'+ message.text +'"')
            if message.type == 'info':
                continue
            if message.type == 'death':
                if message.dead_player_name == self.name:
                    self.is_alive = False
                self.role.new_dead(message.dead_player_name)
            elif message.type == 'end':
                self.game_end = True
                break

async def main() -> None:
    name = ''.join(random.choice(string.ascii_uppercase) for _ in range(7)) # https://stackoverflow.com/questions/2030053/how-to-generate-random-strings-in-python
    async with grpc.aio.insecure_channel('localhost:50051') as channel:
        stub =  engine_pb2_grpc.EngineServerStub(channel)
        player = RandomPlayer(stub)
        if not await player.join():
            print('Try lately')
            return
        await player.get_players()
        await asyncio.gather(
            player.start_game(),
            player.get_messages()
        )
        

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    asyncio.get_event_loop().run_until_complete(main())

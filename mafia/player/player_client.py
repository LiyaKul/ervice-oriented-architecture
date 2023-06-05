import grpc
import logging
import asyncio
import random
import string

import sys
sys.path.append('../../')
sys.path.append('../../../')
sys.path.append('..')
sys.path.append('.')
import mafia.protos.engine_pb2 as engine_pb2
import mafia.protos.engine_pb2_grpc as engine_pb2_grpc

from roles import *

class Player:
    def __init__(self, stub: engine_pb2_grpc.EngineServerStub):
        self.stub = stub
        self.name = ''.join(random.choice(string.ascii_uppercase) for _ in range(7)) # https://stackoverflow.com/questions/2030053/how-to-generate-random-strings-in-python
        self.request_type = 'day'
        self.action_cond = asyncio.Condition()
        self.checks = dict()
        self.check_name = None

    async def join(self) -> None:
        response = await self.stub.Join(engine_pb2.JoinRequest(name=self.name, text='hello'))
        print(self.name + ': "Received join response: ' + response.text + '"')
        self.id = response.id
        return response.id != -1

    async def get_players(self) -> None:
        response = await self.stub.GetPlayers(engine_pb2.GetPlayersRequest(name=self.name, text='hello'))
        self.players =  response.names.split('%')
        print(self.name + ': "Received players:', self.players, '"')

    async def want_to_start(self):
        response = await self.stub.Start(engine_pb2.StartRequest(name=self.name, text='hello'))
        if not response.started:
            print(self.name + ': "Im not in game :("')
            return False
        print(self.name + ': "I got the %s role!"' % response.role)
        if response.role == 'Sheriff':
            self.role = Sheriff(self.id, self.players)
        elif response.role == 'Mafia':
            self.role = Mafia(self.id, self.players, list(map(int,response.mafias.split('%'))))
        else:
            self.role = Villager(self.id, self.players)
        return response.started

    async def get_notifications(self):
        notifications = self.stub.GameInfo(engine_pb2.InfoRequest(name=self.name, text='hello'))   
        
        async for message in notifications:
            print(self.name + ': "'+ message.text +'"')
            if 'ready to start' in  message.text:
                self.players.append(message.text.split()[0])

    async def generate_messages(self):
        while self.request_type != 'end':
            async with self.action_cond:
                await self.action_cond.wait()
            type = self.request_type
            if type == 'day':
                yield engine_pb2.ActionRequest(name=self.name, text='Vote!', type=type, vote_name=self.role.vote())
            if type == 'check':
                if self.role.check_result(self.check_name):
                    yield engine_pb2.ActionRequest(name=self.name, text='Publish', type=type)
            elif type == 'publish':
                print("The results of the Sheriff's checks:")
                for x in self.checks.split('%'):
                    print(x.split()[0], ':', x.split()[1])
            elif self.role.role == 'Mafia':
                yield engine_pb2.ActionRequest(name=self.name, text='Kill!', type=type, action_name=self.role.action())
            elif self.role.role == 'Sheriff':
                yield engine_pb2.ActionRequest(name=self.name, text='Check!', type=type, action_name=self.role.action())
            else:
                yield engine_pb2.ActionRequest(name=self.name, text='Sleep!', type=type)
        
    async def game_actions(self):
        notifications = self.stub.GameAction(self.generate_messages()) 
        
        async for message in notifications:
            self.request_type = message.type
            self.role.new_dead(message.name)
            print(self.name + ': "'+ message.text +'"')
            if message.type == 'check':
                self.check_name = message.text
            if message.type == 'publish':
                print("The results of the Sheriff's checks:")
                self.checks = message.name
            async with self.action_cond:
                self.action_cond.notify()
            if message.type == 'end':
                break


async def main() -> None:
    name = ''.join(random.choice(string.ascii_uppercase) for _ in range(7)) # https://stackoverflow.com/questions/2030053/how-to-generate-random-strings-in-python
    async with grpc.aio.insecure_channel('localhost:50051') as channel:
        stub =  engine_pb2_grpc.EngineServerStub(channel)
        player = Player(stub)
        if not await player.join():
            print('Try lately')
            return
        await player.get_players()
        await asyncio.gather(
            player.want_to_start(),
            player.get_notifications()
        )
        await player.game_actions()
        

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    asyncio.get_event_loop().run_until_complete(main())

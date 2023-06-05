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
        self.request_type = 'day'
        self.action_cond = asyncio.Condition()
        self.checks = dict()
        self.check_name = None
        print('Enter you name:')
        self.name = input()

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
            self.role = Sheriff(self.id, self.players, self.name)
        elif response.role == 'Mafia':
            self.role = Mafia(self.id, self.players, self.name, list(map(int,response.mafias.split('%'))))
        else:
            self.role = Villager(self.id, self.players, self.name)
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
            print("TYTPE", type)
            if type == 'publish':
                print("The results of the Sheriff's checks:")
                for x in self.checks.split('%'):
                    print(x.split()[0], ':', x.split()[1])
            if not self.role.is_alive:
                yield engine_pb2.ActionRequest(name=self.name, text='Sleep!', type=type)
                continue
            if type == 'day':
                print('Voting is going on now. Choose a player.')
                name = input()
                while name not in self.players or name == self.name:
                    if name == self.name:
                        print("You can't vote for yourself. Choose another name. List of players:", self.players)
                    else:
                        print("Incorrect name. Choose on from the list:", self.players)
                    name = input()
                yield engine_pb2.ActionRequest(name=self.name, text='Vote!', type=type, vote_name=name)
            elif type == 'check':
                print('Check results.', self.check_name, 'was', self.check_result)
                name = input()
                if self.role.check_result(self.check_result):
                    print('Do you want publish checks results? Write yes or no.')
                    answer = input()
                    if answer.lower() == 'yes':
                        yield engine_pb2.ActionRequest(name=self.name, text='Publish', type=type)

            elif self.role.role == 'Mafia':
                print('Choose a mafia victim.')
                name = input()
                while name not in self.players or name == self.name or name in self.role.dead_players or name in self.role.mafias:
                    print('!!', name)
                    if name == self.name:
                        print("You can't kill yourself. Choose another name. List of players:", self.players)
                    elif name not in self.players:
                        print("Incorrect name. Choose on from the list:", self.players)
                    elif name in self.role.dead_players:
                        print("Player is dead. Choose another name. Dead players:", self.role.dead_players)
                    else:
                        print("Incorrect name. You can't choose another mafia. List of the mafias:", self.role.mafias)
                    name = input()
                yield engine_pb2.ActionRequest(name=self.name, text='Kill!', type=type, action_name=name)
            elif self.role.role == 'Sheriff':
                print('Choose a player to check the role.')
                name = input()
                while name not in self.players or name == self.name or name in self.role.dead_players:
                    if name == self.name:
                        print("You can't check yourself. Choose another name. List of players:", self.players)
                    elif name not in self.players:
                        print("Incorrect name. Choose on from the list:", self.players)
                    else:
                        print("Player is dead. Choose another name. Dead players:", self.role.dead_players)
                    name = input()
                self.check_name = name
                yield engine_pb2.ActionRequest(name=self.name, text='Check!', type=type, action_name=name)
            else:
                yield engine_pb2.ActionRequest(name=self.name, text='Sleep!', type=type)
        
    async def game_actions(self):
        notifications = self.stub.GameAction(self.generate_messages()) 
        
        async for message in notifications:
            self.request_type = message.type
            if message.name in self.players:
                self.role.new_dead(message.name)
            if message.type == '':
                print(self.name + ': "'+ message.text +'"')
                continue
            print(self.name + ': "'+ message.text +'"')
            if message.type == 'check':
                self.check_result = message.text
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
        print('Do you want to join the game? Write yes or no.')
        answer = input()
        if answer.lower() == 'yes':
            if not await player.join():
                print('Try lately')
        await player.get_players()
        print('Are you ready to start the game? Write yes or no.')
        answer = input()
        if answer.lower() == 'yes':
            print('Good! Waiting for other players...')
            await asyncio.gather(
                player.want_to_start(),
                player.get_notifications()
            )
        await player.game_actions()
        

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    asyncio.get_event_loop().run_until_complete(main())

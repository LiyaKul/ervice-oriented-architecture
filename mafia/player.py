import grpc
import logging
import asyncio
import random
import string
from enum import Enum

import protos.engine_pb2 as engine_pb2
import protos.engine_pb2_grpc as engine_pb2_grpc

from roles import *

class MessageType(Enum):
    INFO = 1
    DEATH = 2
    PUBLISH = 3
    END = 4

class Player:
    def __init__(self, stub: engine_pb2_grpc.EngineServerStub, name = None):
        self.stub = stub
        if name is None or name == '':
            self.name = ''.join(random.choice(string.ascii_uppercase) for _ in range(7))
        else:
            self.name = name
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
            print('Choose a mafia victim.')
            name = input()
            while name not in self.players or name == self.name or name in self.role.dead_players or name in self.role.mafias:
                if name == self.name:
                    print("You can't kill yourself. Choose another name. List of players: ", self.players)
                elif name not in self.players:
                    print("Incorrect name. Choose on from the list:", self.players)
                elif name in self.role.dead_players:
                    print("Player is dead. Choose another name. Dead players: ", self.role.dead_players)
                else:
                    print("Incorrect name. You can't choose another mafia. List of the mafias: ", self.role.mafias)
                name = input()
            response = await self.stub.Kill(engine_pb2.KillRequest(name=self.name, kill_name=name))
            logging.info(self.name + ': ' + response.text)

    async def check(self):
        if self.role.role == 'Sheriff':
            print('Choose a player to check the role.')
            name = input()
            while name not in self.players or name == self.name or name in self.role.dead_players:
                if name == self.name:
                    print("You can't check yourself. Choose another name. List of players: ", self.players)
                elif name not in self.players:
                    print("Incorrect name. Choose on from the list: ", self.players)
                else:
                    print("Player is dead. Choose another name. Dead players: ", self.role.dead_players)
                name = input()
            response = await self.stub.Check(engine_pb2.CheckRequest(name=self.name, check_name=name))
            logging.info(self.name + ': ' + response.text)

    async def vote(self):
        print('Voting is going on now. Choose a player.')
        name = input()
        while name not in self.players or name == self.name:
            if name == self.name:
                print("You can't vote for yourself. Choose another name. List of players: ", self.players)
            elif name not in self.players:
                print("Incorrect name. Choose on from the list:", self.players)
            else:
                print("Player is dead. Choose another name. Dead players: ", self.role.dead_players)
            name = input()
        response = await self.stub.Vote(engine_pb2.VoteRequest(name=self.name, vote_name=name))
        logging.info(self.name + ': ' + response.text)
    
    async def end_day(self):
        response = await self.stub.EndDay(engine_pb2.EndDayRequest(name=self.name))
        if response.ended:
            self.time = 'night'
            if response.text == 'end':
                self.game_end = True
            if response.dead_player_name:
                self.role.new_dead(response.dead_player_name)
                if response.dead_player_name == self.name:
                    self.is_alive = False

    
    async def end_night(self):
        response = await self.stub.EndNight(engine_pb2.EndNightRequest(name=self.name))
        if response.ended:
            self.time = 'day'
            if response.text == 'end':
                self.game_end = True
            if response.dead_player_name:
                self.role.new_dead(response.dead_player_name)
                if response.dead_player_name == self.name:
                    self.is_alive = False
    
    async def start_game(self):
        print('Are you ready to start the game? Write yes or no.')
        answer = input()
        if answer.lower() == 'yes':
            print('Good! Waiting for other players...')
            if not await self.want_to_start():
                exit()
        else:
            exit()
        await asyncio.sleep(1)
        for i in range(20):
            if not self.is_alive or self.game_end:
                break
            if self.time == 'night':
                if self.role.role == 'Sheriff':
                    await self.check()
                    await asyncio.sleep(1)
                elif self.role.role == 'Mafia':
                    await self.kill()
                    await asyncio.sleep(1)
                await self.end_night()
                await asyncio.sleep(1)
                self.time = 'day'
            elif self.time == 'day':
                await self.vote()
                await asyncio.sleep(1)
                await self.end_day()
                await asyncio.sleep(1)
                self.time = 'night'
        if not self.game_end:
            logging.info(self.name + ': Too many iterations, game ended.')

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
    async with grpc.aio.insecure_channel('172.18.0.2:50051') as channel:
        stub =  engine_pb2_grpc.EngineServerStub(channel)
        print('Enter your name.')
        name = input()
        player = Player(stub, name)
        print('Do you want to join the game? Write yes or no.')
        answer = input()
        if answer.lower() == 'yes':
            if not await player.join():
                print('Try lately')
                exit()
        else:
            exit()
        await player.get_players()
        await asyncio.gather(
            player.start_game(),
            player.get_messages()
        )
        

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    asyncio.get_event_loop().run_until_complete(main())

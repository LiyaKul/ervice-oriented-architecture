import grpc
from enum import Enum
from concurrent import futures
import random
import operator

import logging
import asyncio
from typing import AsyncIterable, Iterable

import sys
sys.path.append('../../')
sys.path.append('../')
sys.path.append('../../../')
sys.path.append('.')
import mafia.protos.engine_pb2 as engine_pb2
import mafia.protos.engine_pb2_grpc as engine_pb2_grpc

class State(Enum):
    PENDING = 1
    STARTED = 2
    ENDED = 3

class EngineServer(engine_pb2_grpc.EngineServer):

    def __init__(self) -> None:
        self.players = dict()
        self.current_id = 0
        self.status = State.PENDING
        self.cond = asyncio.Condition()
        self.current_message = ''
        self.notify_cond = asyncio.Condition()
        self.roles_indexes = ['Sheriff', 'Mafia', 'Villager', 'Villager']
        self.mafias = []
        self.players_count = 4
        self.actions_count = 0
        self.day_count = 0
        self.type = 'day'
        self.dead_players = []
        self.action_cond = asyncio.Condition()
        self.votes = dict()
        self.first_player = ''
        self.vote_name = ''
        self.game_count = 0
        self.log_name = ''
        self.roles = dict()
        self.is_publish = False
        self.checks = str()

    def name_to_role(self, name):
        return self.roles_indexes[self.players[name]-1]

    def set_roles_indexes(self):
        logging.info('roles assignment...')
        random.shuffle(self.roles_indexes)
        for i in range(len(self.roles_indexes)):
            if self.roles_indexes[i] == 'Mafia':
                self.mafias.append(str(i+1))
        for name, id in self.players.items():
            self.roles[name] = self.roles_indexes[id - 1]
    
    def handle_vote(self, request: engine_pb2.ActionRequest) -> None:
        if request.vote_name == '':
            return
        if self.type == 'night' and self.roles_indexes[self.players[request.name]-1] != 'Mafia':
            return
        if request.name in self.dead_players:
            return
        if request.vote_name in self.votes.keys():
            self.votes[request.vote_name] += 1
        else:
            self.votes[request.vote_name] = 1

    def vote_result(self) -> str:
        max_name = ''
        max_count = 0
        for name, count in self.votes.items():
            if max_count < count:
                max_name = name
                max_count = count

        for name, count in self.votes.items():
            if max_name != name and max_count == count:
                return ''
        return max_name
    
    def check_game_end(self) -> str:
        alive_mafias = 0
        alive_villagers = 0
        for name in self.players.keys():
            if name in self.dead_players:
                continue
            if self.roles_indexes[self.players[name]-1] == 'Mafia':
                alive_mafias += 1
            else:
                alive_villagers += 1
        logging.info('Alive mafias: ' + str(alive_mafias))
        logging.info('Alive villagers: ' + str(alive_villagers))
        if alive_mafias == 0:
            return 'Villagers'
        if alive_mafias >= alive_villagers:
            return 'Mafias'
        return ''


    async def Join(self, request: engine_pb2.JoinRequest, unused_context) -> engine_pb2.JoinResponse:
        logging.info(request.name + ' want to join')
        if request.name in self.players.values():
            return engine_pb2.JoinResponse(id=-1, text='You have been joined!')
        if self.status == State.STARTED:
            return engine_pb2.JoinResponse(id=-1, text='Game started, try lately!')

        if self.status == State.ENDED:
            return engine_pb2.JoinResponse(id=-1, text='Game ended, try lately!')
        
        self.current_id += 1
        self.players[request.name] = self.current_id
        if self.current_id > 1:
            self.current_message = request.name + ' joined!'
            async with self.notify_cond:
                self.notify_cond.notify_all()
        return engine_pb2.JoinResponse(id=self.current_id, text='Successfully joined!')

    async def GetPlayers(self, request: engine_pb2.GetPlayersRequest, unused_context) -> engine_pb2.GetPlayersResponse:
        logging.info(request.name + ' want to get list of players')
        return engine_pb2.GetPlayersResponse(count=len(self.players), text='Players', names='%'.join(_ for _ in self.players.keys()))

    async def Start(self, request: engine_pb2.StartRequest, unused_context) -> engine_pb2.StartResponse:
        logging.info(request.name + ' ready to start!')
        if self.status == State.ENDED:
            return engine_pb2.StartResponse(started=False, text='Game ended, try lately!')
        self.current_message = request.name + ' ready to start!'
        async with self.notify_cond:
            self.notify_cond.notify_all()
        if len(self.players) == 4:
            logging.info('%d players are recruited, starting game...' % len(self.players))
            self.status = State.STARTED
            self.set_roles_indexes()
            async with self.cond:
                self.cond.notify_all()
        else:
            async with self.cond:
                await self.cond.wait()
        role = self.roles_indexes[self.players[request.name]-1]
        if role == 'Mafia':
            return engine_pb2.StartResponse(started=True, role=role, text='Game is starting!', mafias='%'.join(self.mafias))
        return engine_pb2.StartResponse(started=True, role=role, text='Game is starting!')
    
    async def GameInfo(self, unused_request: engine_pb2.InfoRequest, unused_context) -> AsyncIterable[engine_pb2.InfoResponse]:
        while self.status != State.STARTED:
            async with self.notify_cond:
                await self.notify_cond.wait()
            yield engine_pb2.InfoResponse(text=self.current_message)
    
    async def GameAction(self, request_iterator: AsyncIterable[engine_pb2.ActionRequest], unused_context) -> AsyncIterable[engine_pb2.ActionResponse]:
        yield engine_pb2.ActionResponse(text='Game started!', type='day')
        async for request in request_iterator:
            if self.status == State.ENDED:
                break
            if self.game_count > 10 * self.players_count:
                logging.info('Too many iterations, game is ending...')
                self.status = State.ENDED
                yield engine_pb2.ActionResponse(text='Draw! Game ended.', type='end')
                continue

            if request.text == 'Vote!':
                if request.vote_name == '':
                    logging.info(request.name + ' is undecided about the player to vote!')
                else:
                    logging.info(request.name + ' vote for ' + request.vote_name + '!')
            elif request.text == 'Kill!':
                if request.action_name == '':
                    logging.info(request.name + ' is undecided about the player to kill!')
                else:
                    logging.info(request.name + ' want to kill ' + request.action_name + '!')
            elif request.text == 'Check!':
                if request.action_name == '':
                    logging.info(request.name + ' is undecided about the player to check!')
                else:
                    logging.info(request.name + ' want to check ' + request.action_name + '!')
                    yield engine_pb2.ActionResponse(text=self.roles[request.action_name], type='check')
                    self.checks += '%' + request.action_name + ' ' + self.roles[request.action_name]
            elif request.text == 'Publish!':
                self.is_publish = True

            # if request.type != self.type:
            #     yield engine_pb2.ActionResponse(text='Incorrect message!', name='')
            #     continue
            self.actions_count += 1
            self.handle_vote(request)
            if self.actions_count < self.players_count:
                async with self.action_cond:
                    await self.action_cond.wait()
                if self.is_publish:
                    logging.info(request.name + ": The sheriff decided to share the results of the checks!")
                    yield engine_pb2.ActionResponse(text="The sheriff decided to share the results of the checks!", type='publish', name=self.checks)
            else:
                self.game_count += 1
                self.vote_name = self.vote_result()
                self.actions_count = 0
                self.votes = dict()
                self.log_name = request.name
                async with self.action_cond:
                    self.action_cond.notify_all()
                if self.is_publish:
                    yield engine_pb2.ActionResponse(text="The sheriff decided to share the results of the inspections!", type='publish')
            if self.type == 'day':
                # DAY
                if self.vote_name == '':
                    logging.info(request.name + ": The day's vote failed. Peace day is declared.")
                    yield engine_pb2.ActionResponse(text="The day's vote failed. Peace day is declared.", type='')
                else:
                    logging.info(request.name + ": Results of the day's voting: " + self.vote_name + " was killed!" )
                    self.dead_players.append(self.vote_name)
                    yield engine_pb2.ActionResponse(text="Results of the day's voting: " + self.vote_name + " was killed!" , type='', name=self.vote_name)
            else:
                # NIGHT
                if self.vote_name == '':
                    if self.log_name == request.name:
                        logging.info(request.name + ": The mafia couldn't make a choice")
                    yield engine_pb2.ActionResponse(text="The mafia couldn't make a choice", type='')
                else:
                    self.dead_players.append(self.vote_name)
                    logging.info(request.name + ": %s was killed tonight!" % self.vote_name)
                    yield engine_pb2.ActionResponse(text="%s was killed tonight!" % self.vote_name, type='', name=self.vote_name)
            if self.check_game_end() != '':
                self.status = State.ENDED
                if self.check_game_end() == 'Mafias':
                    logging.info(request.name + ": Mafia wins! Game ended.")
                    yield engine_pb2.ActionResponse(text='Mafia wins! Game ended.', type='end')
                    continue
                else:
                    logging.info(request.name + ": Villagers wins! Game ended.")
                    yield engine_pb2.ActionResponse(text='Villagers wins! Game ended.', type='end')
                    continue
            else:
                if self.type == 'day':
                    logging.info(request.name + ': The city goes to sleep, the mafia wakes up...')
                    yield engine_pb2.ActionResponse(text='The city goes to sleep, the mafia wakes up...', type='night')
                else:
                    logging.info(request.name + ': The mafia goes to sleep, the city wakes up...')
                    yield engine_pb2.ActionResponse(text='The mafia goes to sleep, the city wakes up...', type='day')
            if self.log_name == request.name:
                if self.type == 'day':
                    self.type = 'night'
                else:
                    self.type = 'day'

async def serve():
    server = grpc.aio.server(futures.ThreadPoolExecutor(max_workers=10))
    engine_pb2_grpc.add_EngineServerServicer_to_server(
        EngineServer(), server)
    server.add_insecure_port("[::]:50051")
    logging.info("Starting server")
    await server.start()
    await server.wait_for_termination()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    asyncio.run(serve())

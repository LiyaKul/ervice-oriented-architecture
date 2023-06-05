import grpc
from concurrent import futures
import random
import operator

import logging
import asyncio
from typing import AsyncIterable

import sys
sys.path.append('../../')
sys.path.append('../')
sys.path.append('../../../')
sys.path.append('.')
import mafia.protos.engine_pb2 as engine_pb2
import mafia.protos.engine_pb2_grpc as engine_pb2_grpc

from game import *

class EngineServer(engine_pb2_grpc.EngineServer):

    def __init__(self) -> None:
        self.players = dict()
        self.current_id = 0
        self.cond = asyncio.Condition()
        self.players_count = 4
        self.games = []
        self.player_to_game = dict()

    def set_roles_indexes(self, game_index: int):
        logging.info('roles assignment...')
        self.games[game_index].set_role_indexes()

    def check_game_end(self, game_index) -> str:
        alive_mafias, alive_villagers = self.games[game_index].check_game_end()
        logging.info('Alive mafias: ' + str(alive_mafias))
        logging.info('Alive villagers: ' + str(alive_villagers))
        if alive_mafias == 0:
            return 'Villagers'
        if alive_mafias >= alive_villagers:
            return 'Mafias'
        return ''
    
    def get_game(self, name):
        if name in self.player_to_game.keys():
            return self.player_to_game[name]
        for game in self.games:
            if not game.is_full:
                game.append_player(name)
                self.player_to_game[name] = game.id
                return game.id
        self.games.append(Game(len(self.games())))
        game = self.games[-1]
        game.append_player(name)
        self.player_to_game[name] = game.id
        return game.id


    async def Join(self, request: engine_pb2.JoinRequest, unused_context) -> engine_pb2.JoinResponse:
        logging.info(request.name + ' want to join')
        game = self.get_game(request.name)
        if request.name in self.players.values():
            return engine_pb2.JoinResponse(id=-1, text='You have been joined!')

        if self.status == State.ENDED:
            return engine_pb2.JoinResponse(id=-1, text='Game ended, try lately!')
        
        self.current_id += 1
        if len(game.players)> 1:
            game.current_message = request.name + ' joined!'
            async with game.notify_cond:
                game.notify_cond.notify_all()
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
                    self.handle_vote(request)
                    logging.info(request.name + ' vote for ' + request.vote_name + '!')
            elif request.text == 'Kill!':
                if request.action_name == '':
                    logging.info(request.name + ' is undecided about the player to kill!')
                else:
                    self.handle_vote(request)
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
            if self.actions_count < self.players_count:
                async with self.action_cond:
                    await self.action_cond.wait()
                if self.is_publish:
                    if self.log_name == request.name:
                        logging.info("The sheriff decided to share the results of the checks!")
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
                    if self.log_name == request.name:
                        logging.info("The day's vote failed. Peace day is declared.")
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
                    if self.log_name == request.name:
                        logging.info("%s was killed tonight!" % self.vote_name)
                    yield engine_pb2.ActionResponse(text="%s was killed tonight!" % self.vote_name, type='', name=self.vote_name)
            if self.check_game_end() != '':
                self.status = State.ENDED
                if self.check_game_end() == 'Mafias':
                    if self.log_name == request.name:
                        logging.info(": Mafia wins! Game ended.")
                    yield engine_pb2.ActionResponse(text='Mafia wins! Game ended.', type='end')
                    continue
                else:
                    logging.info(request.name + ": Villagers wins! Game ended.")
                    yield engine_pb2.ActionResponse(text='Villagers wins! Game ended.', type='end')
                    continue
            else:
                if self.type == 'day':
                    if self.log_name == request.name:
                        logging.info('The city goes to sleep, the mafia wakes up...')
                    yield engine_pb2.ActionResponse(text='The city goes to sleep, the mafia wakes up...', type='night')
                else:
                    if self.log_name == request.name:
                        logging.info(': The mafia goes to sleep, the city wakes up...')
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

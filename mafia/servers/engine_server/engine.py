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

    def __init__(self, players_count = 4) -> None:
        self.players = dict()
        self.current_id = 0
        self.players_count = players_count
        self.games = []
        self.player_to_game = dict()

    def set_roles_indexes(self, game_index: int):
        self.games[game_index].set_role_indexes()

    def check_game_end(self, game_index, name) -> str:
        alive_mafias, alive_villagers = self.games[game_index].check_game_end()
        if self.games[game_index].log_name == name:
            logging.info('GAME №' + str(game_index) + ': Alive mafias: ' + str(alive_mafias))
            logging.info('GAME №' + str(game_index) + ': Alive villagers: ' + str(alive_villagers))
        if alive_mafias == 0:
            return 'Villagers'
        if alive_mafias >= alive_villagers:
            return 'Mafias'
        return ''
    
    def get_game(self, name):
        if name in self.player_to_game.keys():
            return self.games[self.player_to_game[name]]
        for game in self.games:
            if not game.is_full:
                game.append_player(name)
                self.player_to_game[name] = game.id
                return game
        self.games.append(Game(len(self.games)))
        game = self.games[-1]
        game.append_player(name)
        self.player_to_game[name] = game.id
        return game


    async def Join(self, request: engine_pb2.JoinRequest, unused_context) -> engine_pb2.JoinResponse:
        logging.info(request.name + ' want to join')
        game = self.get_game(request.name)
        if request.name in self.players.values():
            return engine_pb2.JoinResponse(id=-1, text='You have been joined!')

        if game.status == State.ENDED:
            return engine_pb2.JoinResponse(id=-1, text='Game ended, try lately!')
        
        self.current_id += 1
        if len(game.players) > 1:
            game.current_message = request.name + ' joined!'
            async with game.notify_cond:
                game.notify_cond.notify_all()
        return engine_pb2.JoinResponse(id=self.current_id, text='Successfully joined!')

    async def GetPlayers(self, request: engine_pb2.GetPlayersRequest, unused_context) -> engine_pb2.GetPlayersResponse:
        logging.info(request.name + ' want to get list of players')
        game = self.get_game(request.name)
        return engine_pb2.GetPlayersResponse(count=len(self.players), text='Players', names='%'.join(_ for _ in game.players))

    async def Start(self, request: engine_pb2.StartRequest, unused_context) -> engine_pb2.StartResponse:
        logging.info(request.name + ' ready to start!')
        game = self.get_game(request.name)
        if game.status == State.ENDED:
            return engine_pb2.StartResponse(started=False, text='Game ended, try lately!')
        game.current_message = request.name + ' ready to start!'
        game.start_count += 1
        async with game.notify_cond:
            game.notify_cond.notify_all()
        if game.start_count == game.max_players:
            logging.info('%d players are recruited, starting game...' % game.start_count)
            game.status = State.STARTED
            logging.info('roles assignment...')
            game.set_roles_indexes()
            async with game.cond:
                game.cond.notify_all()
        else:
            async with game.cond:
                await game.cond.wait()
        role = game.roles[request.name]
        if role == 'Mafia':
            return engine_pb2.StartResponse(started=True, role=role, text='Game is starting!', mafias='%'.join(game.mafias))
        return engine_pb2.StartResponse(started=True, role=role, text='Game is starting!')
    
    async def GameInfo(self, request: engine_pb2.InfoRequest, unused_context) -> AsyncIterable[engine_pb2.InfoResponse]:
        game = self.get_game(request.name)
        while game.status != State.STARTED:
            async with game.notify_cond:
                await game.notify_cond.wait()
            yield engine_pb2.InfoResponse(text=game.current_message)
    
    async def GameAction(self, request_iterator: AsyncIterable[engine_pb2.ActionRequest], unused_context) -> AsyncIterable[engine_pb2.ActionResponse]:
        yield engine_pb2.ActionResponse(text='Game started! No voting on the first day.', type='')
        yield engine_pb2.ActionResponse(text='The city goes to sleep, the mafia wakes up...', type='night')
        async for request in request_iterator:
            # logging.info('!!! ' + request.type)

            game = self.get_game(request.name)
            game_name = 'GAME №' + str(game.id)
            if game.status == State.ENDED:
                break
            if game.actions_count == 0:
                game.log_name = request.name
            if game.day_count == 0:
                if game.log_name == request.name:
                    logging.info(game_name + ': Game started! No voting on the first day.')
                    logging.info(game_name + ': The city goes to sleep, the mafia wakes up...')
            if game.actions_count > 10 * game.max_players:
                if request.vote_name == '':
                    logging.info(game_name +': Too many iterations, game is ending...')
                game.status = State.ENDED
                yield engine_pb2.ActionResponse(text='Draw! Game ended.', type='end')
                continue

            if request.text == 'Vote!':
                if request.vote_name == '':
                    logging.info(game_name + ': ' + request.name + ' is undecided about the player to vote!')
                else:
                    game.handle_vote(request)
                    logging.info(game_name + ': ' + request.name + ' vote for ' + request.vote_name + '!')
            elif request.text == 'Kill!':
                if request.action_name == '':
                    logging.info(game_name + ': ' + request.name + ' is undecided about the player to kill!')
                else:
                    game.handle_vote(request)
                    logging.info(game_name + ': ' + request.name + ' want to kill ' + request.action_name + '!')
            elif request.text == 'Check!':
                if request.action_name == '':
                    logging.info(game_name + ': ' + request.name + ' is undecided about the player to check!')
                else:
                    logging.info(game_name + ': ' + request.name + ' want to check ' + request.action_name + '!')
                    yield engine_pb2.ActionResponse(text=game.roles[request.action_name], type='check')
                    game.checks += '%' + request.action_name + ' ' + game.roles[request.action_name]
            elif request.text == 'Publish!':
                game.is_publish = True

            game.actions_count += 1
            if game.actions_count < game.max_players:
                async with game.action_cond:
                    await game.action_cond.wait()
                if game.is_publish:
                    if game.log_name == request.name:
                        logging.info(game_name + ': ' + "The sheriff decided to share the results of the checks!")
                    yield engine_pb2.ActionResponse(text="The sheriff decided to share the results of the checks!", type='publish', name=game.checks)
            else:
                game.vote_name = game.vote_result()
                game.actions_count = 0
                game.votes = dict()
                async with game.action_cond:
                    game.action_cond.notify_all()
                if game.is_publish:
                    yield engine_pb2.ActionResponse(text="The sheriff decided to share the results of the inspections!", type='publish')
            if game.type == 'day':
                # DAY
                if game.vote_name == '':
                    if game.log_name == request.name:
                        logging.info(game_name + ': ' + "The day's vote failed. Peace day is declared.")
                    yield engine_pb2.ActionResponse(text="The day's vote failed. Peace day is declared.", type='')
                else:
                    if game.log_name == request.name:
                        logging.info(game_name + ": Results of the day's voting: " + game.vote_name + " was killed!" )
                    game.dead_players.append(game.vote_name)
                    yield engine_pb2.ActionResponse(text="Results of the day's voting: " + game.vote_name + " was killed!" , type='', name=game.vote_name)
            else:
                # NIGHT
                if game.vote_name == '':
                    if game.log_name == request.name:
                        logging.info(game_name + ": The mafia couldn't make a choice")
                    yield engine_pb2.ActionResponse(text="The mafia couldn't make a choice", type='')
                else:
                    game.dead_players.append(game.vote_name)
                    if game.log_name == request.name:
                        logging.info(game_name + ": %s was killed tonight!" % game.vote_name)
                    yield engine_pb2.ActionResponse(text="%s was killed tonight!" % game.vote_name, type='', name=game.vote_name)
            check_game = self.check_game_end(game.id, request.name)
            if check_game != '':
                game.status = State.ENDED
                if check_game == 'Mafias':
                    if game.log_name == request.name:
                        logging.info(game_name +  ": Mafia wins! Game ended.")
                    yield engine_pb2.ActionResponse(text='Mafia wins! Game ended.', type='end')
                    continue
                else:
                    if request.vote_name == '':
                        logging.info(game_name + ": Villagers wins! Game ended.")
                    yield engine_pb2.ActionResponse(text='Villagers wins! Game ended.', type='end')
                    continue
            else:
                if game.type == 'day':
                    if game.log_name == request.name:
                        game.type = 'night'
                        game.day_count += 1
                        logging.info(game_name + ': The city goes to sleep, the mafia wakes up...')
                    yield engine_pb2.ActionResponse(text='The city goes to sleep, the mafia wakes up...', type='night')
                else:
                    if game.log_name == request.name:
                        game.type = 'day'
                        game.day_count += 1
                        logging.info(game_name + ': The mafia goes to sleep, the city wakes up...')
                    yield engine_pb2.ActionResponse(text='The mafia goes to sleep, the city wakes up...', type='day')

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

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

    def __init__(self, max_players = 4) -> None:
        self.players = dict()
        self.current_id = 0
        self.max_players = max_players
        self.games = []
        self.player_to_game = dict()
        self.end_cond = dict()
        self.start_cond = dict()

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

    def new_game(self):
        self.games.append(Game(len(self.games)))
        game = self.games[-1]
        self.end_cond[game.id] = asyncio.Condition()
        self.start_cond[game.id] = asyncio.Condition()
    
    def get_game(self, name):
        if name in self.player_to_game.keys():
            return self.games[self.player_to_game[name]]
        for game in self.games:
            if not game.is_full:
                game.append_player(name)
                self.player_to_game[name] = game.id
                return game
        self.new_game()
        game = self.games[-1]
        game.append_player(name)
        self.player_to_game[name] = game.id
        return game
    
    def check_game(self, name):
        return name in self.player_to_game.keys()

    async def Join(self, request: engine_pb2.JoinRequest, unused_context) -> engine_pb2.JoinResponse:
        if request.name in self.players.values():
            return engine_pb2.JoinResponse(id=-1, text='Select another name.')

        logging.info(request.name + ' want to join')

        self.players[request.name] = self.current_id
        self.current_id += 1
        game = self.get_game(request.name)
        return engine_pb2.JoinResponse(id=self.players[request.name], text='Successfully joined! Your game number: %d' % game.id)

    async def Leave(self, request: engine_pb2.LeaveRequest, unused_context) -> engine_pb2.LeaveResponse:
        if not self.check_game(request.name):
            return engine_pb2.LeaveResponse(text='You are not in game.')

        logging.info(request.name + ' want to leave game')

        del self.players[request.name]
        game = self.get_game(request.name)
        game.leave(request.name)
        return engine_pb2.LeaveResponse(text='You left the game.')

    async def GetPlayers(self, request: engine_pb2.GetPlayersRequest, unused_context) -> engine_pb2.GetPlayersResponse:
        if not self.check_game(request.name):
            return engine_pb2.GetPlayersResponse(text='You are not in game.')
        game = self.get_game(request.name)
        return engine_pb2.GetPlayersResponse(text='List of players.', names='%'.join(_ for _ in game.players))

    async def Start(self, request: engine_pb2.StartRequest, unused_context) -> engine_pb2.StartResponse:
        if request.name not in self.players.keys():
            return engine_pb2.StartResponse(text='You did not join for the game.')
        game = self.get_game(request.name)
        if game.status == State.ENDED:
            return engine_pb2.StartResponse(started=False, text='Game ended, try lately')
        result = game.inc_start(request.name)
        if result == 'wait':
            logging.info('GAME №' + str(game.id) + ': ' + request.name + ' ready to start!')
            async with self.start_cond[game.id]:
                await self.start_cond[game.id].wait()
        elif result == 'start':
            game.set_roles()
            logging.info('GAME №' + str(game.id) + ': ' + request.name + ' ready to start!')
            async with self.start_cond[game.id]:
                self.start_cond[game.id].notify_all()
            logging.info('GAME №' + str(game.id) + ': %d players are recruited, starting game...' % game.count())
            print(game.roles)
            logging.info('GAME №' + str(game.id) + ': roles assignment...')
        else:
            return engine_pb2.StartResponse(started=False, text=result)

        print(game.roles)
        role = game.roles[request.name]
        if role == 'Mafia':
            return engine_pb2.StartResponse(started=True, role=role, text='Game is starting!', mafias='%'.join(game.mafias))
        return engine_pb2.StartResponse(started=True, role=role, text='Game is starting!')
    
    # async def GameInfo(self, request: engine_pb2.InfoRequest, unused_context) -> AsyncIterable[engine_pb2.InfoResponse]:
    #     game = self.get_game(request.name)
    #     async for notification in game.notifications():
    #         yield engine_pb2.InfoResponse(
    #             type=notification.type,
    #             text=notification.text
    #         )
    
    async def Kill(self, request: engine_pb2.KillRequest, unused_context) -> engine_pb2.KillResponse:
        if not self.check_game(request.name):
            return engine_pb2.KillResponse(text='You are not in game.')
        game = self.get_game(request.name)
        result = game.kill(request)
        if result == 'success':
            return engine_pb2.KillResponse(result=True, text='Your choice has been processed')
        return engine_pb2.KillResponse(result=False, text=result)
    
    async def Check(self, request: engine_pb2.CheckRequest, unused_context) -> engine_pb2.CheckResponse:
        if not self.check_game(request.name):
            return engine_pb2.KillResponse(text='You are not in game.')
        game = self.get_game(request.name)
        result = game.check(request)
        if result not in game.players:
            return engine_pb2.CheckResponse(result=False, text=result)
        return engine_pb2.CheckResponse(result=True, role=result)

    async def Vote(self, request: engine_pb2.VoteRequest, unused_context) -> engine_pb2.VoteResponse:
        if not self.check_game(request.name):
            return engine_pb2.KillResponse(text='You are not in game.')
        game = self.get_game(request.name)
        result = game.vote(request)
        if result == 'success':
            return engine_pb2.VoteResponse(result=True, text='Your choice has been processed')
        return engine_pb2.VoteResponse(result=False, text=result)
    
    async def EndDay(self, request: engine_pb2.EndDayRequest, unused_context) -> engine_pb2.EndDayResponse:
        if not self.check_game(request.name):
            return engine_pb2.EndDayResponse(text='You are not in game.')
        game = self.get_game(request.name)
        if game.time() != 'day':
            return engine_pb2.EndDayResponse(text='It is night now.')
        result = game.inc_end(request.name)
        if result == 'wait':
            logging.info('GAME №' + game.id + ': ' + request.name + ' want to end day!')
            async with self.end_cond[game.id]:
                await self.end_cond[game.id].wait()
            if vote_name == '':
                return engine_pb2.EndDayResponse(ended=True, text="The day's vote failed. Peace day is declared.\nThe city goes to sleep, the mafia wakes up...")
            else:
                return engine_pb2.EndDayResponse(ended=True, text= ": Results of the day's voting: " + vote_name + " was killed!\nThe city goes to sleep, the mafia wakes up...")
        elif result == 'start':
            logging.info('GAME №' + str(game.id) + ': ' + request.name + ' all alive players want to end day!')
            async with self.end_cond[game.id]:
                self.end_cond[game.id].notify_all()
            game.set_night()
            vote_name = game.vote_or_kill_result()
            if vote_name == '':
                logging.info('GAME №' + str(game.id) + ": The day's vote failed. Peace day is declared.")
                logging.info('GAME №' + str(game.id) + ": The city goes to sleep, the mafia wakes up...")
                return engine_pb2.EndDayResponse(ended=True, text="The day's vote failed. Peace day is declared.\nThe city goes to sleep, the mafia wakes up...")
            else:
                game.append_dead_player(vote_name)
                alive_mafias, alive_villagers = game.check_end()
                logging.info('GAME №' + str(game.id) + ": Alive mafias: " + alive_mafias)
                logging.info('GAME №' + str(game.id) + ": Alive villagers: " + alive_villagers)
                if alive_mafias >= alive_villagers:
                    game.set_end()
                    logging.info('GAME №' + str(game.id) + ': Mafia wins! Game ended.')
                    return engine_pb2.EndDayResponse(ended=True, text='Mafia wins! Game ended.')
                if alive_mafias == 0:
                    game.set_end()
                    logging.info('GAME №' + str(game.id) + ': Villagers wins! Game ended.')
                    return engine_pb2.EndDayResponse(ended=True, text='Villagers wins! Game ended.')
                logging.info('GAME №' + str(game.id) + ": The city goes to sleep, the mafia wakes up...")
                return engine_pb2.EndDayResponse(ended=True, text="The city goes to sleep, the mafia wakes up...")
        else:
            return engine_pb2.EndDayResponse(ended=False, text=result)
    
    async def PublishSheriffChecks(self, request: engine_pb2.PublishRequest, unused_context) -> engine_pb2.PublishResponse:
        if not self.check_game(request.name):
            return engine_pb2.KillResponse(text='You are not in game.')
        game = self.get_game(request.name)
        result = game.publish()
        if type(result) == str:
            return engine_pb2.PublishResponse(result=False, text=result)
        # TODO notification
        return engine_pb2.PublishResponse(result=True)

    async def EndNight(self, request: engine_pb2.EndNightRequest, unused_context) -> engine_pb2.EndNightResponse:
        if not self.check_game(request.name):
            return engine_pb2.EndNightResponse(text='You are not in game.')
        game = self.get_game(request.name)
        if game.time() != 'day':
            return engine_pb2.EndNightResponse(text='It is day now.')
        result = game.inc_end(request.name)
        if result == 'wait':
            async with self.end_cond[game.id]:
                await self.end_cond[game.id].wait()
            kill_name = game.vote_or_kill_result()
            if kill_name == '':
                return engine_pb2.EndNightResponse(ended=True, text="The mafia couldn't make a choice\nThe mafia goes to sleep, the city wakes up...")
            else:
                return engine_pb2.EndNightResponse(ended=True, text=  kill_name + " was killed tonight!\nThe mafia goes to sleep, the city wakes up...")
        elif result == 'start':
            async with self.end_cond[game.id]:
                self.end_cond[game.id].notify_all()
                kill_name = game.vote_or_kill_result()
                if kill_name == '':
                    logging.info('GAME №' + str(game.id) +  ": The mafia couldn't make a choice")
                    logging.info('GAME №' + str(game.id) + ": The mafia goes to sleep, the city wakes up...")
                    return engine_pb2.EndNightResponse(ended=True, text="The mafia couldn't make a choice\nThe mafia goes to sleep, the city wakes up...")
                else:
                    logging.info('GAME №' + game.id +  ": %s was killed tonight!" % kill_name)
                    game.append_dead_player(kill_name)
                    alive_mafias, alive_villagers = game.check_end()
                    logging.info('GAME №' + str(game.id) + ": Alive mafias: " + alive_mafias)
                    logging.info('GAME №' + str(game.id) + ": Alive villagers: " + alive_villagers)
                    if alive_mafias >= alive_villagers:
                        game.set_end()
                        logging.info('GAME №' + str(game.id) + ': Mafia wins! Game ended.')
                        return engine_pb2.EndNightResponse(ended=True, text='Mafia wins! Game ended.')
                    if alive_mafias == 0:
                        game.set_end()
                        logging.info('GAME №' + str(game.id) + ': Villagers wins! Game ended.')
                        return engine_pb2.EndNightResponse(ended=True, text='Villagers wins! Game ended.')
                    logging.info('GAME №' + str(game.id) + ": The mafia goes to sleep, the city wakes up...")
                    return engine_pb2.EndNightResponse(ended=True, text="The mafia goes to sleep, the city wakes up...")
        else:
            return engine_pb2.EndNightResponse(ended=False, text=result)

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

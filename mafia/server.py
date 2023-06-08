import grpc
from concurrent import futures
import logging
import asyncio
from typing import AsyncIterable
import os

import protos.engine_pb2 as engine_pb2
import protos.engine_pb2_grpc as engine_pb2_grpc

from game import *

class Message:
    def __init__(self, type, text, dead_player_name=None):
        self.type = type
        self.text = text
        self.dead_player_name = dead_player_name

class EngineServer(engine_pb2_grpc.EngineServer):

    def __init__(self, max_players = 4) -> None:
        self.players = dict()
        self.current_id = 0
        self.max_players = max_players
        self.games = []
        self.player_to_game = dict()
        self.end_cond = dict()
        self.start_cond = dict()

        self.messages = dict()

    def set_roles_indexes(self, game_index: int):
        self.games[game_index].set_role_indexes()
        logging.info('GAME №' + str(game_index) + ': set roles:' + str(self.games[game_index].roles))

    def new_game(self):
        self.games.append(Game(len(self.games)))
        game = self.games[-1]
        self.end_cond[game.id] = asyncio.Condition()
        self.start_cond[game.id] = asyncio.Condition()
        self.messages[game.id] = []
    
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
    
    def is_alive(self, request):
        game = self.get_game(request.name)
        return request.name not in game.dead_players

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
        self.messages[game.id].append(Message('info', request.name + ' left game'))
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
            self.messages[game.id].append(Message('info', request.name + ' ready to start!'))
            logging.info('GAME №' + str(game.id) + ': ' + request.name + ' ready to start!')
            async with self.start_cond[game.id]:
                await self.start_cond[game.id].wait()
        elif result == 'start':
            game.set_roles()
            self.messages[game.id].append(Message('info', request.name + ' ready to start!'))
            logging.info('GAME №' + str(game.id) + ': ' + request.name + ' ready to start!')
            async with self.start_cond[game.id]:
                self.start_cond[game.id].notify_all()
            self.messages[game.id].append(Message('info', '%d players are recruited, starting game...' % game.max_players))
            logging.info('GAME №' + str(game.id) + ': %d players are recruited, starting game...' % game.max_players)
            self.messages[game.id].append(Message('info', 'roles assignment...'))
            logging.info('GAME №' + str(game.id) + ': roles assignment...')
            self.messages[game.id].append(Message('info', 'The game started!'))
            logging.info('GAME №' + str(game.id) + ': The game started!')
        else:
            return engine_pb2.StartResponse(started=False, text=result)

        role = game.roles[request.name]
        if role == 'Mafia':
            return engine_pb2.StartResponse(started=True, role=role, text='The game started!', players='%'.join(game.players), mafias='%'.join(game.mafias))
        return engine_pb2.StartResponse(started=True, role=role, text='The game started!', players='%'.join(game.players))
    
    async def generate_messages(self, game_id):
        current_index = 0
        while True:
            if len(self.messages[game_id]) > 0 and self.messages[game_id][-1] == 'end':
                break
            if current_index >= len(self.messages[game_id]):
                await asyncio.sleep(0)
                continue
            yield self.messages[game_id][current_index]
            current_index += 1
            
    
    async def GameInfo(self, request: engine_pb2.InfoRequest, unused_context) -> AsyncIterable[engine_pb2.InfoResponse]:
        game_id = self.get_game(request.name).id
        async for message in self.generate_messages(game_id):
            yield engine_pb2.InfoResponse(
                type=message.type,
                text=message.text
            )
    
    async def Kill(self, request: engine_pb2.KillRequest, unused_context) -> engine_pb2.KillResponse:
        if not self.check_game(request.name):
            return engine_pb2.KillResponse(text='You are not in game.')
        if not self.is_alive(request):
            return engine_pb2.KillResponse(text='You are ghost.')
        game = self.get_game(request.name)
        result = game.kill(request)
        if result == 'success':
            logging.info('GAME №' + str(game.id) + ': Mafia ' + request.name + ' want to kill ' + request.kill_name)
            return engine_pb2.KillResponse(result=True, text='Your choice has been processed')
        return engine_pb2.KillResponse(result=False, text=result)
    
    async def Check(self, request: engine_pb2.CheckRequest, unused_context) -> engine_pb2.CheckResponse:
        if not self.check_game(request.name):
            return engine_pb2.KillResponse(text='You are not in game.')
        if not self.is_alive(request):
            return engine_pb2.KillResponse(text='You are ghost.')
        game = self.get_game(request.name)
        result = game.check(request)
        logging.info('GAME №' + str(game.id) + ': Sheriff ' + request.name + ' want to check ' + request.check_name)
        return engine_pb2.CheckResponse(result=True, role=result)

    async def Vote(self, request: engine_pb2.VoteRequest, unused_context) -> engine_pb2.VoteResponse:
        if not self.check_game(request.name):
            return engine_pb2.KillResponse(text='You are not in game.')
        if not self.is_alive(request):
            return engine_pb2.KillResponse(text='You are ghost.')
        game = self.get_game(request.name)
        result = game.vote(request)
        logging.info('GAME №' + str(game.id) + ': ' + request.name + ' want to vote for ' + request.vote_name)
        if result == 'success':
            return engine_pb2.VoteResponse(result=True, text='Your choice has been processed')
        return engine_pb2.VoteResponse(result=False, text=result)
    
    async def EndDay(self, request: engine_pb2.EndDayRequest, unused_context) -> engine_pb2.EndDayResponse:
        if not self.check_game(request.name):
            return engine_pb2.EndDayResponse(text='You are not in game.')
        if not self.is_alive(request):
            return engine_pb2.KillResponse(text='You are ghost.')
        game = self.get_game(request.name)
        result = game.inc_end(request.name)
        if result == 'wait':
            logging.info('GAME №' + str(game.id) + ': ' + request.name + ' want to end day!')
            async with self.end_cond[game.id]:
                await self.end_cond[game.id].wait()
            vote_name = game.vote_or_kill_result()
            if vote_name == '':
                return engine_pb2.EndDayResponse(ended=True)
            else:
                return engine_pb2.EndDayResponse(ended=True, dead_player_name=vote_name)
        elif result == 'start':
            logging.info('GAME №' + str(game.id) + ': ' + request.name + ' want to end day!')
            logging.info('GAME №' + str(game.id) + ': all alive players want to end day!')
            logging.info('GAME №' + str(game.id) + ': Voting result: ' + str(game.votes))
            async with self.end_cond[game.id]:
                self.end_cond[game.id].notify_all()
            vote_name = game.vote_or_kill_result()
            if vote_name == '':
                self.messages[game.id].append(Message('info', "The day's voting failed. Peace day is declared."))
                self.messages[game.id].append(Message('info', "The city goes to sleep, the mafia wakes up..."))
                logging.info('GAME №' + str(game.id) + ": The day's voting failed. Peace day is declared.")
                logging.info('GAME №' + str(game.id) + ": The city goes to sleep, the mafia wakes up...")
                return engine_pb2.EndDayResponse(ended=True)
            else:
                self.messages[game.id].append(Message('death', "Results of the day's voting: " + vote_name + " was killed!"))
                logging.info('GAME №' + str(game.id) + ": Results of the day's voting: " + vote_name + " was killed!")
                game.append_dead_player(vote_name)
                game.set_night()
                alive_mafias, alive_villagers = game.check_game_end()
                logging.info('GAME №' + str(game.id) + ": Alive mafias: " + str(alive_mafias))
                logging.info('GAME №' + str(game.id) + ": Alive villagers: " + str(alive_villagers))
                if alive_mafias >= alive_villagers:
                    game.set_end()
                    self.messages[game.id].append(Message('end', "Mafia wins! Game ended."))
                    logging.info('GAME №' + str(game.id) + ': Mafia wins! Game ended.')
                    return engine_pb2.EndDayResponse(ended=True, text='end', dead_player_name=vote_name)
                if alive_mafias == 0:
                    game.set_end()
                    self.messages[game.id].append(Message('end', "Villagers wins! Game ended."))
                    logging.info('GAME №' + str(game.id) + ': Villagers wins! Game ended.')
                    return engine_pb2.EndDayResponse(ended=True, text='end', dead_player_name=vote_name)
                self.messages[game.id].append(Message('info', "The city goes to sleep, the mafia wakes up..."))
                logging.info('GAME №' + str(game.id) + ": The city goes to sleep, the mafia wakes up...")
                return engine_pb2.EndDayResponse(ended=True, dead_player_name=vote_name)
        else:
            return engine_pb2.EndDayResponse(ended=False, text=result)
    
    async def PublishSheriffChecks(self, request: engine_pb2.PublishRequest, unused_context) -> engine_pb2.PublishResponse:
        if not self.check_game(request.name):
            return engine_pb2.KillResponse(text='You are not in game.')
        if not self.is_alive(request):
            return engine_pb2.KillResponse(text='You are ghost.')
        game = self.get_game(request.name)
        result = game.publish()
        # TODO
        if type(result) == str:
            return engine_pb2.PublishResponse(result=False, text=result)
        self.messages[game.id].append(Message('publish', result))
        return engine_pb2.PublishResponse(result=True)

    async def EndNight(self, request: engine_pb2.EndNightRequest, unused_context) -> engine_pb2.EndNightResponse:
        if not self.check_game(request.name):
            return engine_pb2.EndNightResponse(text='You are not in game.')
        if not self.is_alive(request):
            return engine_pb2.KillResponse(text='You are ghost.')
        game = self.get_game(request.name)
        result = game.inc_end(request.name)
        if result == 'wait':
            async with self.end_cond[game.id]:
                await self.end_cond[game.id].wait()
            kill_name = game.vote_or_kill_result()
            if kill_name == '':
                return engine_pb2.EndNightResponse(ended=True)
            else:
                return engine_pb2.EndNightResponse(ended=True, dead_player_name=kill_name)
        elif result == 'start':
            async with self.end_cond[game.id]:
                self.end_cond[game.id].notify_all()
            kill_name = game.vote_or_kill_result()
            if kill_name == '':
                self.messages[game.id].append(Message('info', "The mafia couldn't make a choice"))
                self.messages[game.id].append(Message('info', "The mafia goes to sleep, the city wakes up..."))
                logging.info('GAME №' + str(game.id) +  ": The mafia couldn't make a choice")
                logging.info('GAME №' + str(game.id) + ": The mafia goes to sleep, the city wakes up...")
                return engine_pb2.EndNightResponse(ended=True)
            else:
                self.messages[game.id].append(Message('death', kill_name + ' was killed tonight!'))
                logging.info('GAME №' + str(game.id) +  ": %s was killed tonight!" % kill_name)
                game.append_dead_player(kill_name)
                game.set_day()
                alive_mafias, alive_villagers = game.check_game_end()
                logging.info('GAME №' + str(game.id) + ": Alive mafias: " + str(alive_mafias))
                logging.info('GAME №' + str(game.id) + ": Alive villagers: " + str(alive_villagers))
                if alive_mafias >= alive_villagers:
                    game.set_end()
                    self.messages[game.id].append(Message('end', 'Mafia wins! Game ended.'))
                    logging.info('GAME №' + str(game.id) + ': Mafia wins! Game ended.')
                    return engine_pb2.EndNightResponse(ended=True, text='end', dead_player_name=kill_name)
                if alive_mafias == 0:
                    game.set_end()
                    self.messages[game.id].append(Message('end', 'Villagers wins! Game ended.'))
                    logging.info('GAME №' + str(game.id) + ': Villagers wins! Game ended.')
                    return engine_pb2.EndNightResponse(ended=True, text='end', dead_player_name=kill_name)
                self.messages[game.id].append(Message('info', 'The mafia goes to sleep, the city wakes up...'))
                logging.info('GAME №' + str(game.id) + ": The mafia goes to sleep, the city wakes up...")
                return engine_pb2.EndNightResponse(ended=True)
        else:
            return engine_pb2.EndNightResponse(ended=False, text=result)

async def serve():
    server = grpc.aio.server(futures.ThreadPoolExecutor(max_workers=10))
    engine_pb2_grpc.add_EngineServerServicer_to_server(
        EngineServer(), server)
    
    server.add_insecure_port('172.18.0.2:50051')
    logging.info("Starting server")
    await server.start()
    await server.wait_for_termination()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    asyncio.run(serve())

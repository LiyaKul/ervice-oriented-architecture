import random

class Villager:
    def __init__(self, id, players, name):
        self.players_count = 4
        self.id = id - 1
        self.dead_players = []
        self.is_alive = True
        self.players = players
        self.role = 'Villager'
        self.name = name
    
    def vote(self) -> int:
        if not self.is_alive:
            return ''
        vote_name = self.id
        for i in range(3):
            if vote_name != self.id and vote_name not in self.dead_players:
                return self.players[vote_name]
            vote_name = random.choice(list(range(4)))
        return ''
    
    def new_dead(self, name: str) -> None:
        if name == '':
            return
        for i in range(self.players_count):
            if self.players[i] == name:
                self.dead_players.append(i)
        if name == self.name:
            self.is_alive = False
            print('You was killed! Now you are the ghost! You can watch the game.')

    
    def action(self) -> str:
        return ''


class Sheriff(Villager):
    def __init__(self, id, players, name):
        super().__init__(id, players, name)
        self.checked_players = []
        self.role = 'Sheriff'
        self.roles = dict()
    
    def action(self) -> str:
        if not self.is_alive:
            return ''
        check_id = self.id
        for i in range(3):
            if check_id != self.id and check_id not in self.dead_players and check_id not in self.roles.keys():
                self.checked_players.append(check_id)
                return self.players[check_id]
            check_id = random.choice(list(range(4)))
        return ''
    
    def check_result(self, res: str) -> None:
        self.roles[self.checked_players[-1]] = res
        if res == 'Mafia':
            return bool(random.randint(0, 1)) # 0 - publish data, 1 - not publish data

class Mafia(Villager):
    def __init__(self, id, players, name, mafias = []):
        super().__init__(id, players, name)
        self.mafias = mafias
        self.role = 'Mafia'

    def action(self) -> str:
        if not self.is_alive:
            return ''
        kill_id = self.id
        for i in range(3):
            if kill_id != self.id and kill_id not in self.dead_players and kill_id not in self.mafias:
                return self.players[kill_id]
            kill_id = random.choice(list(range(4)))
        return ''
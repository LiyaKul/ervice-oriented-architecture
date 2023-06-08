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
        random.seed(name)
    
    def vote(self) -> int:
        if not self.is_alive:
            return ''
        vote_id = random.randint(0, self.players_count - 1)
        for i in range(50):
            vote_name = self.players[vote_id]
            if vote_name != self.name and vote_name not in self.dead_players:
                return vote_name
            vote_id = random.randint(0, self.players_count - 1)
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
        check_id = random.randint(0, self.players_count - 1)
        for i in range(50):
            check_name = self.players[check_id]
            if check_name != self.name and check_name not in self.dead_players and check_name in self.players:
                self.checked_players.append(check_name)
                return check_name
            check_id= random.randint(0, self.players_count - 1)
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
        kill_id = random.randint(0, self.players_count - 1)
        for i in range(50):
            kill_name = self.players[kill_id]
            if kill_name != self.name and kill_name not in self.dead_players and kill_name not in self.mafias and kill_name in self.players:
                return kill_name
            kill_id= random.randint(0, self.players_count - 1)
        return ''
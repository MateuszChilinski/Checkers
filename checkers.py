from enum import Enum
import numpy as np
import math
import random
import time
import pickle

eps = 0.001
C = 0.5
class Checker(Enum):
    NotAllowed = -1
    Empty = 0
    White = 1
    WhiteKing = 2
    Red = 3
    RedKing = 4

class PlayerColour(Enum):
    Red = 1
    White = 2

class GameStatus(Enum):
    InProgress = 0
    RedWon = 1
    WhiteWon = 2
    Tie = 3

class MovePossibilities(Enum):
    Impossible = 0
    Possible = 1
    AttackRequired = 2

def ConvToEnumShort(num):
    if(num == -1):
        return "   "
    elif(num == 0):
        return "   "
    elif(num == 1):
        return " W "
    elif(num == 2):
        return " Q " # queen - whites
    elif(num == 3):
        return " R "
    elif(num == 4):
        return " K " # king - reds
    else:
        return "ERROR"

def calculateDistance(x1,y1,x2,y2):  
     dist = (x2 - x1)**2 + (y2 - y1)**2  
     return dist  

class Game:
    # reds are first
    def __init__(self, board=None, currPlay=None):
        self.movesC = 0
        self.board = np.array(np.repeat(0,64))
        self.currentPlayer = PlayerColour.Red.value
        if(currPlay is not None):
            self.currentPlayer = currPlay
        for i in range(1, 9):
            if(i % 2 == 1):
                self.board[8*(i-1):8*i:2] = Checker.NotAllowed.value
                if(i < 4):
                    self.board[8*(i-1)+1:8*i+1:2] = Checker.White.value
                if(i > 5):
                    self.board[8*(i-1)+1:8*i+1:2] = Checker.Red.value

            elif(i % 2 == 0):
                self.board[8*(i-1)+1:8*i+1:2] = Checker.NotAllowed.value
                if(i < 4):
                    self.board[8*(i-1):8*i:2] = Checker.White.value
                if(i > 5):
                    self.board[8*(i-1):8*i:2] = Checker.Red.value


        self.board = self.board.reshape((8,8))
        
        if(board is not None):
            self.board = np.copy(board)
        
    def PrintBoard(self,fX=-1,fY=-1,hX=-1,hY=-1):
        board_to_print = np.array(np.vectorize(ConvToEnumShort)(self.board), dtype=object)
        if(hX != -1 and hY != -1 and fX != -1 and fY != -1):
            board_to_print[fX,fY] = ("( )")
            board_to_print[hX,hY] = ("(" + str.strip(board_to_print[hX,hY]) + ")")
        print(board_to_print)
        print("")

    def GetAllCurrentPossibleMoves(self):
        moves = list()
        for x in range(0, 8):
            for y in range(0, 8):
                #elf.PrintBoard()
                if((self.currentPlayer == PlayerColour.White.value and (self.board[x,y] == Checker.White.value or self.board[x,y] == Checker.WhiteKing.value)) or 
                    (self.currentPlayer == PlayerColour.Red.value and (self.board[x,y] == Checker.Red.value or self.board[x,y] == Checker.RedKing.value))):
                    for move in self.GetPossibleMoves(x,y):
                        #print(move)
                        moves.append((x, y , move[0], move[1], self.currentPlayer))
        return moves


    def GetPossibleMoves(self, fromX, fromY): # x - row y - column
        possible_moves = self.GetAllPossibleMoves(fromX,fromY)
        if(self.board[fromX,fromY] == Checker.White.value or self.board[fromX,fromY] == Checker.WhiteKing.value):
            colour = PlayerColour.White.value
        elif(self.board[fromX,fromY] == Checker.Red.value or self.board[fromX,fromY] == Checker.RedKing.value):
            colour = PlayerColour.Red.value
        else:
            return set()
        if(self.CheckIfPossibleMultipleJump(colour)):
            can_conquest = False
            for (possibleX, possibleY) in possible_moves:
                if(abs(calculateDistance(fromX,fromY,possibleX,possibleY)-8) < eps): 
                    can_conquest = True
                    break
            if(can_conquest):
                return possible_moves
            else:
                return set()
        return possible_moves
    def GetAllPossibleMoves(self, fromX, fromY): # x - row y - column
        possible_moves = set()
        left_top = self.CheckLeftTop(fromX,fromY)
        left_bottom = self.CheckLeftBottom(fromX,fromY)
        right_top = self.CheckRightTop(fromX,fromY)
        right_bottom = self.CheckRightBottom(fromX,fromY)

        if(self.board[fromX,fromY] == Checker.Empty.value or self.board[fromX,fromY] == Checker.NotAllowed.value):
            return possible_moves

        if(self.board[fromX,fromY] == Checker.Red.value or self.board[fromX,fromY] == Checker.RedKing.value or self.board[fromX,fromY] == Checker.WhiteKing.value):
            if(left_top != False):
                possible_moves.add(left_top)
            if(right_top != False):
                possible_moves.add(right_top)

        if(self.board[fromX,fromY] == Checker.White.value or self.board[fromX,fromY] == Checker.WhiteKing.value or self.board[fromX,fromY] == Checker.RedKing.value):
            if(left_bottom != False):
                possible_moves.add(left_bottom)
            if(right_bottom != False):
                possible_moves.add(right_bottom)
        return self.ParsePossibleMoves(fromX,fromY,possible_moves)

    def ParsePossibleMoves(self,fromX,fromY,possible_moves):
        can_conquest = False
        for (possibleX, possibleY) in possible_moves:
            if(abs(calculateDistance(fromX,fromY,possibleX,possibleY)-8) < eps): 
                can_conquest = True
                break
        if(can_conquest == False):
            return possible_moves
        new_possible_moves = set()
        for (possibleX, possibleY) in possible_moves:
            if(abs(calculateDistance(fromX,fromY,possibleX,possibleY)-8) < eps): 
                new_possible_moves.add((possibleX, possibleY))
        return new_possible_moves

    def CheckFromAnyAngle(self,fromX,fromY,fX,fY,minX,minY):
        if(fromX == minX or fromY == minY): # can't go
            return False
        if(self.board[fromX+fX,fromY+fY] == Checker.Empty.value):
            return (fromX+fX,fromY+fY)
        else:
            if(fromX == minX-fX or fromY == minY-fY): # is blocked so can't attack for sure
                return False
            # check if can attack
            if(self.currentPlayer == PlayerColour.Red.value and (self.board[fromX+fX,fromY+fY] == Checker.White.value or self.board[fromX+fX,fromY+fY] == Checker.WhiteKing.value) and self.board[fromX+2*fX,fromY+2*fY] == Checker.Empty.value):
                # can attack
                return (fromX+2*fX,fromY+2*fY)
            if(self.currentPlayer == PlayerColour.White.value and (self.board[fromX+fX,fromY+fY] == Checker.Red.value or self.board[fromX+fX,fromY+fY] == Checker.RedKing.value) and self.board[fromX+2*fX,fromY+2*fY] == Checker.Empty.value):
                # can attack
                return (fromX+2*fX,fromY+2*fY)
        return False
    def CheckLeftTop(self,fromX, fromY):
        return self.CheckFromAnyAngle(fromX,fromY,-1,-1,0,0)
    def CheckLeftBottom(self,fromX, fromY):
        return self.CheckFromAnyAngle(fromX,fromY,1,-1,7,0)
    def CheckRightBottom(self,fromX, fromY):
        return self.CheckFromAnyAngle(fromX,fromY,1,1,7,7)
    def CheckRightTop(self,fromX, fromY):
        return self.CheckFromAnyAngle(fromX,fromY,-1,1,0,7)

    def CheckIfPossibleMultipleJump(self, colour):
        for x in range(0, 8):
            for y in range(0, 8):
                if((colour == PlayerColour.Red.value and (self.board[x,y] == Checker.Red.value or self.board[x,y] == Checker.RedKing.value)) or 
                   (colour == PlayerColour.White.value and (self.board[x,y] == Checker.White.value or self.board[x,y] == Checker.WhiteKing.value))):
                    possible_moves = self.GetAllPossibleMoves(x,y)
                    for (possibleX, possibleY) in possible_moves:
                        if(abs(calculateDistance(x,y,possibleX,possibleY)-8) < eps):
                            return True
        return False
    def MakeMove(self,fromX, fromY, toX, toY, colour):
        if(colour != self.currentPlayer):
            print(str(colour))
            print(str(self.currentPlayer))
            print("Error - it is not this player's turn!")
            return
        if((self.board[fromX,fromY] == Checker.White.value or self.board[fromX,fromY] == Checker.WhiteKing.value) and colour != PlayerColour.White.value):
            print("Error - it is not this player's turn!")
            return
        if((self.board[fromX,fromY] == Checker.Red.value or self.board[fromX,fromY] == Checker.RedKing.value) and colour != PlayerColour.Red.value):
            print("Error - it is not this player's turn!")
            return
        possible_moves = self.GetPossibleMoves(fromX, fromY)
        if((toX, toY) not in possible_moves):
            print("Error - this move is not possible!")
            return
        # we can multijump elsewhere and we don't do it - don't let player do it then
        if(self.CheckIfPossibleMultipleJump(colour) and abs(calculateDistance(fromX,fromY,toX,toY)-2) < eps):
            print("Error - player attempted to move even though he can attack!")
            return
        next_move_possible = False
        self.movesC = self.movesC+1
        # we can do it - bear in mind that possible moves include the need to conquest
        if(abs(calculateDistance(fromX,fromY,toX,toY)-2) < eps): # no attacks
            self.board[toX,toY] = self.board[fromX,fromY]
            self.board[fromX,fromY] = Checker.Empty.value
        # attack
        elif(abs(calculateDistance(fromX,fromY,toX,toY)-8) < eps): # attack
            next_move_possible = True
            self.board[toX,toY] = self.board[fromX,fromY]
            self.board[fromX,fromY] = self.board[int((fromX+toX)/2),int((fromY+toY)/2)] = Checker.Empty.value
        if(colour == PlayerColour.Red.value and toX == 0):
            #promote to king
            self.board[toX,toY] = Checker.RedKing.value
        if(colour == PlayerColour.White.value and toX == 7):
            #promote to king
            self.board[toX,toY] = Checker.WhiteKing.value
        #self.PrintBoard(fromX,fromY,toX,toY)
        if(next_move_possible):
            possible_moves = self.GetPossibleMoves(toX, toY)
            for (possibleX, possibleY) in possible_moves:
                if(abs(calculateDistance(toX,toY,possibleX,possibleY)-8) < eps): 
                    #player has to make another move
                    return
        self.currentPlayer = PlayerColour.White.value if self.currentPlayer == PlayerColour.Red.value else PlayerColour.Red.value
    def setxy(self,x,y,val):
        self.board[x,y] = val

    def GameStatus(self, heuristic=1):
        if(self.movesC > 100):
            return GameStatus.Tie
        whites = 0
        reds = 0
        if(len(self.GetAllCurrentPossibleMoves()) == 0):
            return GameStatus.Tie
        for x in range(0, 8):
            for y in range(0, 8):
                if(self.board[x,y] == Checker.White.value):
                    whites = whites + 1
                if(self.board[x,y] == Checker.WhiteKing.value):
                    whites = whites + 1
                if(self.board[x,y] == Checker.Red.value):
                    reds = reds + 1
                if(self.board[x,y] == Checker.RedKing.value):
                    reds = reds + 1
        if(whites == 0 or (whites*3 <= reds)):
            return GameStatus.RedWon
        if(reds == 0 or (reds*3 <= whites)):
            return GameStatus.WhiteWon
        if(whites == 1 and reds == 1):
            return GameStatus.Tie
        return GameStatus.InProgress
class Node:
    def __init__(self, parent=None, timesWon=0, timesVisited=0, chosenMove=None, nodes=None, board=None, colour=PlayerColour.Red.value):
        self.parent = parent
        self.timesWon = timesWon
        self.timesVisited = timesVisited
        self.chosenMove = chosenMove
        self.board = board
        self.colour = colour
        if nodes==None:
            self.nodes = list()
        else:
            self.nodes = nodes
    def GetGame(self):
        #moves = self.GetMoves()
        #moves.reverse()
        return Game(self.board, self.colour)


class AI:
    def __init__(self, desiredStatus):
        self.desiredStatus = desiredStatus

    def trainMCTS(self, it):
        self.root = Node()
        self.root.board = Game().board
        for i in range(0, it):
            self.selection(self.root)

    def MakeMove(self, game, colour=None):
        if(not np.array_equal(game.board, self.root.board)):
            for node in self.root.nodes:
                if(np.array_equal(game.board, node.board)):
                    self.root = node
        if(not np.array_equal(game.board, self.root.board)): # double+ attack
            self.root = Node(None, 0, 0, None, None, game.board, colour)
        timeout = time.time() + 0.5
        while True:
            self.selection(self.root)
            self.selection(self.root)
            if time.time() > timeout:
                break
        bestNode = max(self.root.nodes, key=lambda node: node.timesWon)
        self.root = bestNode
        game.MakeMove(bestNode.chosenMove[0], bestNode.chosenMove[1], bestNode.chosenMove[2], bestNode.chosenMove[3], bestNode.chosenMove[4])
        
    def selection(self, node):
        if(len(node.nodes) == 0):
            self.expansion(node)
            return
        bestChild = max(node.nodes, key=lambda nd: self.CalculateUCB(nd))
        self.selection(bestChild)

    def expansion(self, node):
        if(node.GetGame().GameStatus() == GameStatus.InProgress):
            winners = list()
            newMoves = node.GetGame().GetAllCurrentPossibleMoves()
            for move in newMoves:
                curretNodeGameStatus = node.GetGame()
                curretNodeGameStatus.MakeMove(move[0], move[1], move[2], move[3], move[4])
                newNode = Node(node, 0, 0, move, None, curretNodeGameStatus.board, curretNodeGameStatus.currentPlayer)
                node.nodes.append(newNode)
                if(curretNodeGameStatus.GameStatus() == self.desiredStatus):
                    winners.append(newNode)
            if(len(winners) > 0):
                winnerNode = winners[0]
                self.Simulation(winnerNode)
                return
            randomNode = node.nodes[random.randint(0, len(node.nodes)-1)]
            self.Simulation(randomNode)
        else:
            if(node.GetGame().GameStatus() == self.desiredStatus):
                won = 1
            else:
                won = 0
            self.backpropagation(node, won)
    def backpropagation(self, node, won):
        currentNode = node
        while currentNode != None:
            currentNode.timesVisited = currentNode.timesVisited+1
            currentNode.timesWon = currentNode.timesWon+won
            currentNode = currentNode.parent
    def CalculateUCB(self, node):
        if node.timesVisited == 0:
            return math.inf
        return node.timesWon/node.timesVisited + C * math.sqrt(math.log(node.parent.timesVisited) / node.timesVisited)

    def Simulation(self, node):
        gameToSimulate = node.GetGame()
        while(gameToSimulate.GameStatus() == GameStatus.InProgress):
            self.MakeRandomMove(gameToSimulate)
        if(gameToSimulate.GameStatus() == self.desiredStatus):
            won = 1
        else:
            won = 0
        if(gameToSimulate.GameStatus() == GameStatus.Tie):
            won = 0.5
        self.backpropagation(node, won)
            
    def MakeRandomMove(self, game):
        availableMoves = game.GetAllCurrentPossibleMoves()
        randomMove = availableMoves[random.randint(0, len(availableMoves)-1)]
        game.MakeMove(randomMove[0], randomMove[1], randomMove[2], randomMove[3], randomMove[4])

train = 1

if train == 0:
    game = Game()
    print("Initial")
    game.PrintBoard()
    game.MakeMove(5, 0, 4, 1, PlayerColour.Red.value)
    game.MakeMove(2, 1, 3, 2, PlayerColour.White.value)
    game.MakeMove(5, 6, 4, 7, PlayerColour.Red.value)
    game.setxy(7,2,Checker.Empty.value)
    game.MakeMove(3, 2, 5, 0, PlayerColour.White.value)
    game.MakeMove(5, 0, 7, 2, PlayerColour.White.value)
    game.MakeMove(5, 4, 4, 3, PlayerColour.Red.value)
    game.MakeMove(7, 2, 5, 4, PlayerColour.White.value)
    game.MakeMove(5, 4, 3, 2, PlayerColour.White.value)
else:

    redWon = 0
    whiteWon = 0
    ties = 0

    for i in range(0, 1000):
        game = Game()

        ai_red = AI(GameStatus.RedWon)
        ai_white = AI(GameStatus.WhiteWon)

        ai_red.trainMCTS(5)
        ai_white.trainMCTS(5)

        while(game.GameStatus() == GameStatus.InProgress):
            while(game.currentPlayer == PlayerColour.Red.value):
                ai_red.MakeMove(game, PlayerColour.Red.value)
            if(game.GameStatus() != GameStatus.InProgress):
                break
            while(game.currentPlayer == PlayerColour.White.value):
                ai_white.MakeMove(game, PlayerColour.White.value)
        if(game.GameStatus() == GameStatus.RedWon):
            redWon = redWon + 1
        elif(game.GameStatus() == GameStatus.WhiteWon):
            whiteWon = whiteWon + 1
        else:
            ties = ties + 1
        print("Red won: " + str(redWon) + " White won: " + str(whiteWon) + " Ties: " + str(ties))
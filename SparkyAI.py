import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
import cv2
import time
from matplotlib import style

style.use('ggplot')

class TheWorld(object):
    def __init__(self, row, column, firePits, teleports):
        self.grid = np.zeros((row,column))
        self.row = row
        self.column = column
        self.stateSpace = [i for i in range(self.row*self.column)]
        self.stateSpace.remove(self.row*self.column-1)
        self.stateSpaceAll = [i for i in range(self.row*self.column)]
        self.actionSpace = {'U': -self.row, 'D': self.row, 'L': -1, 'R': 1}
        self.actionChoice = ['U', 'D', 'L', 'R']
        self.agentPosition = 0
        self.firePits = firePits
        self.teleports = teleports
    
    def isGoal(self, state):
        return state in self.stateSpaceAll and state not in self.stateSpace
            
    def getFirePitLocation(self, firePit):
        self.firePit = firePit
        x = firePit // self.row
        y = firePit % self.column
        return x, y
            
    def getTeleportLocation(self, teleportIn, teleportOut):
        self.teleportIn = teleportIn
        self.teleportOut = teleportOut
        xIn = teleportIn // self.row
        yIn = teleportIn % self.column
        xOut = teleportOut // self.row
        yOut = teleportOut % self.column
        
        return xIn, yIn, xOut, yOut
    
    def getAgentState(self):
        x = self.agentPosition // self.row
        y = self.agentPosition % self.column
        return x, y
    
    def actionSpaceChoice(self):
        return np.random.choice(self.actionChoice)
    
    def setState(self, state):
        x, y = self.getAgentState()
        self.grid[x][y] = 0
        self.agentPosition = state
        x, y = self.getAgentState()
        self.grid[x][y] = 1
    
    def isOffGrid(self, newState, oldState):
        if newState not in self.stateSpaceAll:
            return True
        elif oldState % self.row == 0 and newState % self.row == self.row -1:
            return True
        elif oldState % self.row == self.row -1 and newState % self.row == 0:
            return True
        else:
            return False
    
    def step(self, action):
        agentX, agentY = self.getAgentState()
        takenStep = self.agentPosition + self.actionSpace[action]
        
        reward = 0
        
        if takenStep in self.firePits:
            takenStep = 0
            reward += -1
            
        if takenStep in self.teleports.keys():
            takenStep = teleports[takenStep]
            
        if not self.isGoal(takenStep):
            reward += -1
        else:
            reward = 0
        
        if not self.isOffGrid(takenStep, self.agentPosition):
            self.setState(takenStep)
            return takenStep, reward, self.isGoal(takenStep), None
        else:
            return self.agentPosition, reward, self.isGoal(self.agentPosition), None
    
    def reset(self):
        self.agentPosition = 0
        return self.agentPosition

def maxAction(Q, state, actions):
    values = np.array([Q[state,a] for a in actions])
    action_idx = np.argmax(values)
    return actions[action_idx]

if __name__ == '__main__':
    firePits = [11, 12]
    teleports = {5: 14, 13:2}
    row = 4
    column = 4
    env = TheWorld(row, column, firePits, teleports)
    
    ALPHA = 0.1
    GAMMA = 1.0
    EPS = 1.0
    
    PLAYER_N = 1
    FIREPIT_N = 2
    GOAL_N = 3
    TELEPORT_IN_N = 4
    TELEPORT_OUT_N = 5
    
    d = {1: (225, 191, 0), 2: (0, 0, 255), 3: (0, 255, 0), 4: (225, 0, 0), 5: (0, 165, 225)}
    
    Q = {}
    for state in env.stateSpaceAll:
        for action in env.actionChoice:
            Q[state, action] = 0
    numOfGames = 50000
    totalRewards = np.zeros(numOfGames)
    totalSteps = np.zeros(numOfGames)
    
    for n in range(numOfGames):
        print('iteration #', n)
        done = False
        epRewards = 0
        stepsTaken = 0
        pos = env.reset()
        while not done:
            rand = np.random.random()
            if rand < (1-EPS):
                action = maxAction(Q, pos, env.actionChoice)
            else:
                action = env.actionSpaceChoice()
            
            pos_new, reward, done, info = env.step(action)
            action_new = maxAction(Q, pos_new, env.actionChoice)
            Q[pos, action] = (1-ALPHA)*Q[pos, action] + ALPHA*(reward + GAMMA*Q[pos_new, action_new])
            
            '''rendering...'''
            render = np.zeros((row, column, 3), dtype=np.uint8)
            for pit in firePits:
                x, y = env.getFirePitLocation(pit)
                render[x][y] = d[FIREPIT_N]
            for teleport in teleports:
                xIn, yIn, xOut, yOut = env.getTeleportLocation(teleport, teleports[teleport])
                render[xIn][yIn] = d[TELEPORT_IN_N]
                render[xOut][yOut] = d[TELEPORT_OUT_N]
            agentX, agentY = env.getAgentState();
            render[agentX][agentY] = d[PLAYER_N]
            render[row-1][column-1] = d[GOAL_N]
            
            img = Image.fromarray(render, "RGB")
            img = img.resize((800, 800))
            cv2.imshow("SparkyAI", np.array(img))
            
            if reward==-2:
                if cv2.waitKey(250) & 0xFF == ord('s'):
                    break
            elif reward==0:
                if cv2.waitKey(500) & 0xFF == ord('s'):
                    break
            else:
                if cv2.waitKey(5) & 0xFF == ord('s'):
                    break
            '''done rendering'''
            
            
            pos = pos_new
            epRewards += reward
            stepsTaken = stepsTaken+1
            
            
            #can't render and show table at same time so have to comment one off
            
            
            '''creating data frame of q table and showing it
            print('Showing Q Table for Every Step')
            
            print('Agent Went :', action)
            
            list_ = []
            for s in range(16):
                sub_l = [Q[s, 'U'], Q[s, 'D'], Q[s, 'L'], Q[s, 'R']]
                list_.append(sub_l)
                index = [i for i in range(16)]
                column = ['U', 'D', 'L', 'R']
                
            df = pd.DataFrame(list_, index, column)
            print(df)
            
            time.sleep(1)
            done showing'''
            
            
        if EPS - 1/numOfGames > 0:
            EPS -= 1/numOfGames
        else:
            EPS = 0
            
        print('Total Steps taken to reach the goal: ', stepsTaken)
        print('Total Rewards recieved', epRewards)
        
        totalRewards[n] = epRewards
        totalSteps[n] = stepsTaken
        
    #creating subplot for STEPS TAKEN & REWARD OVER TIME
    plt.figure(1)
    plt.plot(totalSteps)
    plt.xlabel("# of Iteration")
    plt.ylabel("# of Steps Taken")
    plt.title("Steps Taken Over Time")
    plt.show()
    plt.figure(2)
    plt.plot(totalRewards)
    plt.xlabel("# of Iteration")
    plt.ylabel("# of Rewards Gained")
    plt.title("Rewards Gained Over Time")
    plt.show()

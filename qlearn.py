import numpy as np
import gym
import gym_dpp

def QLearning(env, learning, discount, epsilon, min_eps, episodes, interval):
    gridsize = env.gridsize
    num_actions = len(env.actions)
    # Initialize Q table
    Q = np.random.uniform(low = -1, high = 1, size = (gridsize, gridsize, num_actions)) #height, width, num actions
    
    # Initialize variables 
    reward_list = []
    step_list = []
    max_reward = 0

    # Calculate episodic reduction in epsilon
    reduction = (epsilon - min_eps)/episodes
    
    # Run Q learning algorithm
    for i in range(episodes):
        # Initialize parameters
        done = False
        tot_reward, reward, episode_count= 0,0,0
        state = env.reset()
        temp_steps = []

        while done != True:   
            # Determine next action - epsilon greedy strategy
            if np.random.random() < 1 - epsilon:
                action = np.argmax(Q[state[0], state[1]]) 
            else:
                action = np.random.randint(0, num_actions-1)
                
            # Get next state and reward, store action number            
            state2, reward, done, info = env.step(action) 
            temp_steps.append(action)
            
            #Allow for terminal states
            if done and state2[0] >= 0.5:
                Q[state[0], state[1], action] = reward
                
            # Adjust Q value for current state
            else:
                delta = learning*(reward + discount*np.max(Q[state2[0], state2[1]]) - 
                                 Q[state[0], state[1],action])
                Q[state[0], state[1],action] += delta
                                     
            # Update variables
            tot_reward += reward
            state = state2
        
        # Decay epsilon
        if epsilon > min_eps:
            epsilon -= reduction
        
        # Track rewards
        reward_list.append(tot_reward)
        if tot_reward > max_reward:
            max_reward = tot_reward
            step_list = temp_steps
        
            
        if (i+1) % interval == 0:    
            print('Episode {} Max Reward: {}. final prob'.format(i+1, max_reward), env.priors)
            if i+1 < episodes:
                env.render(step_list, "Episode: " + str(i+1), "Max Reward: " + '%.2f' % max_reward, False) #render
            else:
                env.render(step_list, "Episode: " + str(i+1), "Max Reward: " + '%.2f' % max_reward, True) #render
        episode_count += 1
            
    env.close()
    
    return 

env = gym.make('dpp-v3')
agent_pos, goal_pos = env.reset()

# (environment, learning, discount, epsilon, min episodes, max episodes, render interval) 
QLearning(env, 0.8, 0.9, 0.8, 0, 10000, 2500)


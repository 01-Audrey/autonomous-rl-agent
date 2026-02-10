import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.distributions import Categorical
import numpy as np

class PPONetwork(nn.Module):
    """PPO Actor-Critic Network"""
    
    def __init__(self, state_dim, action_dim, hidden_dim):
        super(PPONetwork, self).__init__()
        
        # Shared layers
        self.shared_fc1 = nn.Linear(state_dim, hidden_dim)
        self.shared_fc2 = nn.Linear(hidden_dim, hidden_dim)
        
        # Actor head (policy)
        self.actor_fc = nn.Linear(hidden_dim, action_dim)
        
        # Critic head (value function)
        self.critic_fc = nn.Linear(hidden_dim, 1)
    
    def forward(self, state):
        """Forward pass through network"""
        x = F.relu(self.shared_fc1(state))
        x = F.relu(self.shared_fc2(x))
        
        logits = self.actor_fc(x)
        value = self.critic_fc(x)
        
        return logits, value
    
    def get_action(self, state, deterministic=False):
        """Get action for inference"""
        if isinstance(state, np.ndarray):
            state = torch.FloatTensor(state)
        
        if state.dim() == 1:
            state = state.unsqueeze(0)
        
        with torch.no_grad():
            logits, value = self.forward(state)
            probs = F.softmax(logits, dim=-1)
            
            if deterministic:
                action = torch.argmax(probs, dim=-1)
            else:
                dist = Categorical(probs)
                action = dist.sample()
        
        return action.item(), probs.cpu().numpy().squeeze(), value.item()

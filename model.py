import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
import os

class Model(nn.Module):

    def __init__(self, input_size, hidden_size, output_size):
        super().__init__()

        self.linear1 = nn.Linear(input_size, hidden_size)
        self.linear2 = nn.Linear(hidden_size, output_size)

    def forward(self, x):
        x = F.relu(self.linear1(x))
        x = self.linear2(x)

        return x

    def save(self, file_name='model.pth'):
        model_folder_path = './model'
        if not os.path.exists(model_folder_path):
            os.makedirs(model_folder_path)

        file_name = os.path.join(model_folder_path, file_name)
        torch.save(self.state_dict(), file_name)


class QTrainer:
    def __init__(self, model, lr, gamma):
        self.lr = lr
        self.gamma = gamma
        self.model = model
        self.optimizer = optim.Adam(model.parameters(), lr=self.lr)
        self.criterion = nn.MSELoss()

    def train_move(self, pre_state, move, reward, post_state, alive):
        pre_state = torch.tensor(pre_state, dtype=torch.float)
        post_state = torch.tensor(post_state, dtype=torch.float)
        move = torch.tensor(move, dtype=torch.long)
        reward = torch.tensor(reward, dtype=torch.float)
        # (n, x)

        if len(pre_state.shape) == 1:
            # (1, x)
            pre_state = torch.unsqueeze(pre_state, 0)
            post_state = torch.unsqueeze(post_state, 0)
            move = torch.unsqueeze(move, 0)
            reward = torch.unsqueeze(reward, 0)
            alive = (alive, )

        # 1: predicted Q values with current state
        pred = self.model(pre_state)

        target = pred.clone()
        for idx in range(len(alive)):
            Q_new = reward[idx]
            if not alive[idx]:
                Q_new = reward[idx] + self.gamma * torch.max(self.model(post_state[idx]))

            target[idx][torch.argmax(move[idx]).item()] = Q_new

        # 2: Q_new = r + y * max(next_predicted Q value) -> only do this if not done
        # pred.clone()
        # preds[argmax(action)] = Q_new
        self.optimizer.zero_grad()
        loss = self.criterion(target, pred)
        loss.backward()

        self.optimizer.step()

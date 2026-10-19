from torch.nn import functional as F
from torch import nn


class Model(nn.Module):
    def __init__(self, output_dim):
        super(Model, self).__init__()
        steps = [
            nn.Linear(768, 512),
            nn.ReLU(inplace=True),
            nn.Dropout(0.3),
            # nn.Linear(512, 256),
            # nn.ReLU(inplace=True),
            # nn.Dropout(0.3),
            nn.Linear(512, output_dim),
            nn.Sigmoid(),
        ]

        self.steps = nn.Sequential(*steps)

    def forward(self, x):
        return F.normalize(self.steps(x), p=2, dim=1)
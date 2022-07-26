# AUTOGENERATED! DO NOT EDIT! File to edit: 05 Experiments.ipynb (unless otherwise specified).

__all__ = ['Trainer', 'device', 'visualize_points', 'device', 'save_embedding_visualization', 'collate_loss']

# Cell
import torch.nn as nn
import torch
import time
import datetime
import FRED
from tqdm.notebook import tqdm, trange
import glob
from PIL import Image
import os
from .embed import ManifoldFlowEmbedder
import ipywidgets as widgets
import base64
import matplotlib.pyplot as plt

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")


class Trainer(object):
    def __init__(
        self,
        FE,
        loss_weights,
        dataloader,
        device=device,
        title="Vanilla MFE",
        visualization_functions=[save_embedding_visualization, visualize_points],
    ):
        self.vizfiz = visualization_functions
        self.loss_weights = loss_weights
        self.FE = FE.to(device)
        self.losses = None
        self.dataloader = dataloader
        self.title = title
        self.epochs_between_visualization = 10
        self.timestamp = datetime.datetime.now().isoformat()
        os.mkdir(f"visualizations/{self.timestamp}")
        self.optim = torch.optim.Adam(self.FE.parameters())
        self.scheduler = None
        # for plotting
        self.labels = dataloader.dataset.labels
        self.X = dataloader.dataset.X

    def fit(self, n_epochs=100):
        for epoch_num in trange(n_epochs):
            for data in self.dataloader:
                self.optim.zero_grad()
                # update loss weights according to scheduling
                if self.scheduler is not None:
                    self.loss_weights = self.scheduler(self.loss_weights)
                # have model compute losses, compile them into cost using loss weights
                data['X'] = data['X'].to(device)
                data['P'] = data['P'].to(device)
                data['precomputed distances'] = data['precomputed distances'].to(device)
                losses = self.FE(data, self.loss_weights)
                cost = self.weight_losses(losses)
                # backpropogate and update model
                cost.backward()
                self.optim.step()
                # add losses to running loss history
                self.losses = collate_loss(
                    provided_losses=losses, prior_losses=self.losses
                )
            # run visualizations, if needed
            if epoch_num % self.epochs_between_visualization == 0:
                title = f"{self.timestamp}/{self.title} Epoch {epoch_num:03d}"
                emb_X = self.FE.embedder(self.X)
                flowArtist = self.FE.flowArtist
                self.visualize(emb_X, flowArtist, self.losses, title)
        # Save most recent embedded points and flow artist for running visualizations
        self.embedded_points = self.FE.embedder(self.dataloader.dataset.X)
        self.flow_artist = flowArtist
        self.labels = self.dataloader.dataset.labels

    def weight_losses(self, losses):
        cost = 0
        for loss_name in losses.keys():
            cost += self.loss_weights[loss_name] * losses[loss_name]
        return cost

    def visualize(self, embedded_points, flow_artist, losses, title):
        for viz_f in self.vizfiz:
            viz_f(
                embedded_points=embedded_points,
                flow_artist=flow_artist,
                losses=losses,
                title=title,
                labels=self.labels,
                FE=self.FE,
            )

    def training_gif(self, duration=50):
        file_names = glob.glob(f"visualizations/{self.timestamp}/*.jpg")
        file_names.sort()
        frames = [Image.open(image) for image in file_names]
        frame_one = frames[0]
        frame_one.save(
            f"visualizations/{self.timestamp}/{self.title}.gif",
            format="GIF",
            append_images=frames,
            save_all=True,
            duration=duration,
            loop=0,
        )
        # display in jupyter notebook
        b64 = base64.b64encode(
            open(f"visualizations/{self.timestamp}/{self.title}.gif", "rb").read()
        ).decode("ascii")
        display(widgets.HTML(f'<img src="data:image/gif;base64,{b64}" />'))

    def visualize_embedding(self):
        visualize_points(
            embedded_points=self.embedded_points,
            flow_artist=self.flow_artist,
            labels=self.labels,
            title=self.title,
        )

    def visualize_loss(self, loss_type="all"):
        if loss_type == "all":
            for key in self.losses.keys():
                plt.plot(self.losses[key])
            plt.legend(self.losses.keys(), loc="upper right")
            plt.title("loss")
        else:
            plt.plot(self.losses[loss_type])
            plt.title(loss_type)

# Cell
import torch
from .embed import compute_grid

device = torch.device("cuda" if torch.has_cuda else "cpu")


def visualize_points(
    embedded_points,
    flow_artist,
    labels=None,
    device=device,
    title="FRED's Embedding",
    save=False,
    **kwargs,
):
    # computes grid around points
    # TODO: This might create CUDA errors
    grid = compute_grid(embedded_points.to(device)).to(device)
    # controls the x and y axes of the plot
    # linspace(min on axis, max on axis, spacing on plot -- large number = more field arrows)
    uv = flow_artist(grid).detach().cpu()
    u = uv[:, 0].cpu()
    v = uv[:, 1].cpu()
    x = grid.detach().cpu()[:, 0]
    y = grid.detach().cpu()[:, 1]
    # quiver
    # 	plots a 2D field of arrows
    # 	quiver([X, Y], U, V, [C], **kw);
    # 	X, Y define the arrow locations, U, V define the arrow directions, and C optionally sets the color.
    if labels is not None:
        sc = plt.scatter(
            embedded_points[:, 0].detach().cpu(),
            embedded_points[:, 1].detach().cpu(),
            c=labels,
        )
    # 			plt.legend()
    else:
        sc = plt.scatter(
            embedded_points[:, 0].detach().cpu(), embedded_points[:, 1].detach().cpu()
        )
    plt.suptitle("Flow Embedding")
    plt.quiver(x, y, u, v)
    # Display all open figures.
    if save:
        plt.savefig(f"visualizations/{title}.jpg")
    else:
        plt.show()
    plt.close()


# Cell
def save_embedding_visualization(
    embedded_points,
    flow_artist,
    labels=None,
    device=device,
    title="FRED's Embedding",
    **kwargs
):
    visualize_points(
        embedded_points=embedded_points,
        flow_artist=flow_artist,
        labels=labels,
        device=device,
        title=title,
        save=True,
    )

# Cell
def collate_loss(
    provided_losses,
    prior_losses=None,
    loss_type="total",
):
    # diffusion_loss,reconstruction_loss, smoothness_loss
    k = ""
    if prior_losses is None:
        # if there are no prior losses, initialize a new dictionary to store these
        prior_losses = {}
        for key in provided_losses.keys():
            prior_losses[key] = []
            # k = key
        prior_losses["total"] = []
    for key in provided_losses.keys():
        try:
            prior_losses[key].append(provided_losses[key].detach().cpu().numpy())
        except:
            prior_losses[key].append(0)
    return prior_losses

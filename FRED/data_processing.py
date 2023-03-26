# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/02 Data Utils - Kernels and Diffusion/02d Flow Datasets.ipynb (unless otherwise specified).

__all__ = ['affinity_from_flow', 'affinity_matrix_from_pointset_to_pointset', 'affinity_grid_search',
           'flashlight_affinity_matrix', 'directions_array_from', 'flashlight_cosine_similarity', 'anisotropic_kernel',
           'adaptive_anisotropic_kernel', 'flashlight_kernel', 'make_sparse_safe', 'distance_matrix',
           'anisotropic_kernel', 'adaptive_anisotropic_kernel', 'zero_negligible_thresholds', 'diffusion_matrix',
           'diffusion_matrix_from_points', 'diffusion_coordinates', 'diffusion_map_from_points',
           'diffusion_map_from_affinities', 'plot_3d', 'flow_neighbors', 'ManifoldWithVectorField',
           'dataloader_from_ndarray']

# Cell
import torch
import torch.nn.functional as F


def affinity_from_flow(flow, directions_array, flow_strength=1, sigma=1):
    """Compute probabilities of transition in the given directions based on the flow.

    Parameters
    ----------
    flow : torch tensor of shape n_points x n_dims
        _description_
    directions_array : torch tensor of shape n_directions x n_points x n_dims. Assumed to be normalized.
        _description_
    sigma : int, optional
        kernel bandwidth, by default 1
    returns (n_points)
    """
    assert len(flow.shape) == 2  # flow should only have one dimension
    assert len(directions_array.shape) > 1 and len(directions_array.shape) < 4
    n_directions = directions_array.shape[0]
    # Normalize directions
    length_of_directions = torch.linalg.norm(directions_array, dim=-1)
    normed_directions = F.normalize(directions_array, dim=-1)
    # and normalize flow # TODO: Perhaps reconsider
    # Calculate flow lengths, used to scale directions to flow
    # flow_lengths = torch.linalg.norm(flow,dim=-1)
    if len(directions_array) == 1:  # convert to 2d array if necessary
        directions_array = directions_array[:, None]
    # scale directions to have same norm as flow
    # scaled_directions = normed_directions * flow_lengths[:,None].repeat(directions_array.shape[0],1,directions_array.shape[2])
    # compute dot products as matrix multiplication
    dot_products = (normed_directions * flow).sum(-1)
    # take distance between flow projected onto direction and the direction
    distance_from_flow = (torch.linalg.norm(flow, dim=1)).repeat(
        n_directions, 1
    ) - dot_products
    # take absolute value
    distance_from_flow = torch.abs(distance_from_flow)
    # print('shape of dff',distance_from_flow.shape)
    # add to this the length of each direction
    distance_from_flow = flow_strength * distance_from_flow + length_of_directions
    # put the points on rows, directions in columns
    distance_from_flow = distance_from_flow.T
    # take kernel of distances
    kernel = torch.exp(-distance_from_flow / sigma)
    return kernel

# Cell

def affinity_matrix_from_pointset_to_pointset(
    pointset1, pointset2, flow, n_neighbors=None, sigma=0.5, flow_strength=1
):
    """Compute affinity matrix between the points of pointset1 and pointset2, using the provided flow.

    Parameters
    ----------
    pointset1 : torch tensor, n1 x d
        The first pointset, to calculate affinities *from*
    pointset2 : torch tensor, n2 x d
        The second pointset, to calculate affinities *to* (from pointset1)
    flow : a function that, when called at a point, gives the flow at that point
    n_neighbors : number of neighbors to include in affinity computations. All neighbors beyond it are given affinity zero
    (currently not implemented)

    Returns:
    Affinity matrix: torch tensor of shape n1 x n2
    """

    # Calculate the directions from point i in pointset 1 to point j in pointset 2
    n1 = pointset1.shape[0]
    n2 = pointset2.shape[0]
    P2 = pointset2[:, :, None].repeat(1, 1, n1)
    P1 = pointset1.T.repeat(n2, 1, 1)
    P3 = P2 - P1
    P3 = P3.transpose(1, 2)
    # dimension 1 represents directions to point i
    # dimension 2 represents direction from point j
    # dimension 3 represents direction in each dimension (R^n)
    # compute affinities from flow and directions
    affinities = affinity_from_flow(flow, P3, sigma=sigma, flow_strength=flow_strength)

    return affinities

# Cell
import matplotlib.pyplot as plt

def affinity_grid_search(X,flow,sigmas, flow_strengths):
  fig, axs = plt.subplots(len(sigmas),len(flow_strengths), figsize=(len(flow_strengths*6),len(sigmas)*6))
  X = torch.tensor(X)
  flow = torch.tensor(flow)
  for i, s in enumerate(sigmas):
    for j, f in enumerate(flow_strengths):
      A = affinity_matrix_from_pointset_to_pointset(X, X, flow, sigma=s, flow_strength=f)
      A = A.numpy()
      axs[i][j].set_title(f"$\sigma = {s}$ and $f={f}$")
      axs[i][j].imshow(A)
  plt.show()

# Cell
import torch
import numpy as np
def flashlight_affinity_matrix(X, flow, k=10, sigma="automatic",flow_strength= 1):
    if type(X) == torch.Tensor:
        X = X.numpy()
    Dists = distance_matrix(X)
    if sigma == "automatic":
        sigma = np.median(np.partition(Dists,k)[:,k])
        print("Set sigma = ",sigma)
    # convert back to tensors
    X = torch.Tensor(X)
    flow = torch.Tensor(flow)
    A = affinity_matrix_from_pointset_to_pointset(X, X, flow, sigma=sigma, flow_strength=flow_strength)
    return A

# Cell
def directions_array_from(X):
    """Given n x d tensor X, returns n x n tensor where entry i,j is x_j - x_i. Useful for getting a distance matrix."""
    n1 = X.shape[0]
    P2 = X[:, :, None].repeat(1, 1, n1)
    P1 = X.T.repeat(n1, 1, 1)
    P3 = P1 - P2
    P3 = P3.transpose(1, 2)
    return P3

# Cell
def flashlight_cosine_similarity(X, flow, directions_array = None, eps = 0.01):
    """Computes a localized cosine similarity between the direction xj - xi and the flow at xi. Ideal for use in embedding spaces."""
    # Get directions array of xj - xi
    if directions_array is not None:
        P3 = directions_array
    else:
        P3 = directions_array_from(X)
    # expand array of flows
    flows_expanded = flow.repeat(len(X),1,1).transpose(dim0=0,dim1=1)
    # get norms of each array
    norm_flows = torch.linalg.norm(flows_expanded,dim=2)
    norm_directions = torch.linalg.norm(P3,dim=2)
    # Perform dot product
    dot_prod = (P3 * flows_expanded).sum(dim=2)
    # normalize by norms
    cosine_sim = dot_prod / (torch.max(torch.tensor(eps),norm_flows * norm_directions))
    return cosine_sim

# Cell
def anisotropic_kernel(D, sigma=0.7, alpha = 1):
    """Computes anisotropic kernel of given distances matrix.

    Parameters
    ----------
    D : ndarray or sparse
    sigma : float, optional
      Kernel bandwidth, by default 0.7
    alpha : int, optional
      Degree of density normalization, from 0 to 1; by default 1
    This is a good function.
    """
    W = torch.exp(-D**2/(2*sigma**2))
    # Additional normalization step for density
    D = torch.diag(1/(torch.sum(W,dim=1)**alpha))
    W = D @ W @ D
    return W

# Cell
def adaptive_anisotropic_kernel(D, k=10, alpha = 1):
    # Get the distance to the kth neighbor
    distance_to_k_neighbor = np.partition(D,k)[:,k]
    # Populate matrices with this distance for easy division.
    div1 = np.ones(len(D))[:,None] @ distance_to_k_neighbor[None,:]
    div2 = div1.T
    # compute the gaussian kernel with an adaptive bandwidth
    W = (1/2*np.sqrt(2*np.pi))*(np.exp(-D**2/(2*div1**2))/div1 + np.exp(-D**2/(2*div2**2))/div2)
    # Additional normalization step for density
    D = np.diag(1/(np.sum(W,axis=1)**alpha))
    W = D @ W @ D
    return W

# Cell
def flashlight_kernel(X, flows, kernel_type = "adaptive anisotropic", k=10, sigma = 0.7, anisotropic_density_normalization = 1, flow_strength=1):
    """A distance aware adaptation of the flashlight cosine similarity,
    obtained by multiplying the cosine similarity by a traditional guassian kernel.
    This is not intended to be differentiable, although is with some choices of kernels (anisotropic, plain).
    """
    # send data to tensors
    X = torch.tensor(X)
    flows = torch.tensor(flows)
    # Get flashlight cosine
    DA = directions_array_from(X)
    W_cosine = flashlight_cosine_similarity(X, flows, directions_array=DA)
    # Flow strength must be an odd integer to be symmetric
    assert flow_strength == int(flow_strength) and flow_strength // 2 != flow_strength /2
    W_strengthened_cosine = W_cosine ** flow_strength
    D = torch.linalg.norm(DA, dim=-1)
    if kernel_type == "anisotropic":
        W = anisotropic_kernel(D, sigma=sigma, alpha=anisotropic_density_normalization) # works with pytorch tensors, is theoretically differentiable.
    if kernel_type == "adaptive anisotropic":
        D_np = D.numpy()
        W_np = adaptive_anisotropic_kernel(D_np, k=k, alpha = anisotropic_density_normalization)
        W = torch.tensor(W_np)
    if kernel_type == "fixed":
        W = torch.exp(-D/(sigma**2))
        W = W.fill_diagonal_(0)
    # W = W.detach()
    flashlight_K = W * ((W_strengthened_cosine+1)/2)
    return flashlight_K

# Cell
from scipy.sparse import bsr_array, csr_array
import warnings
def make_sparse_safe(A):
  if type(A) != 'scipy.sparse._arrays.bsr_array':
    warnings.warn("Sparsifying input to bsr_array")
    A = csr_array(A)
  return A

# Cell
from sklearn.metrics import pairwise_distances
def distance_matrix(X, metric = "euclidean"):
    X = make_sparse_safe(X) # converts to csr_array
    D = pairwise_distances(X, metric = metric, n_jobs = -1) # use all of the available cores
    return D


# Cell
def anisotropic_kernel(D, sigma=0.7, alpha = 1):
    """Computes anisotropic kernel of given distances matrix.

    Parameters
    ----------
    D : ndarray or sparse
    sigma : float, optional
      Kernel bandwidth, by default 0.7
    alpha : int, optional
      Degree of density normalization, from 0 to 1; by default 1
    This is a good function.
    """
    W = np.exp(-D**2/(2*sigma**2))
    # Additional normalization step for density
    D = np.diag(1/(np.sum(W,axis=1)**alpha))
    W = D @ W @ D
    return W

# Cell
def adaptive_anisotropic_kernel(D, k=10, alpha = 1):
    # Get the distance to the kth neighbor
    distance_to_k_neighbor = np.partition(D,k)[:,k]
    # Populate matrices with this distance for easy division.
    div1 = np.ones(len(D))[:,None] @ distance_to_k_neighbor[None,:]
    div2 = div1.T
    # compute the gaussian kernel with an adaptive bandwidth
    W = (1/2*np.sqrt(2*np.pi))*(np.exp(-D**2/(2*div1**2))/div1 + np.exp(-D**2/(2*div2**2))/div2)
    # Additional normalization step for density
    D = np.diag(1/(np.sum(W,axis=1)**alpha))
    W = D @ W @ D
    return W

# Cell
def zero_negligible_thresholds(A, threshold = 1e-5):
    A = make_sparse_safe(A)
    sparse_A_2 = A.copy()
    sparse_A_2 /= threshold
    sparse_A_2 = sparse_A_2.floor()
    sparse_A_2 /= sparse_A_2.max()
    sparse_A_2 = sparse_A_2.ceil()
    return A * sparse_A_2

# Cell
from scipy.sparse import diags
def diffusion_matrix(A,symmetric=False,return_degree=False):
  A = make_sparse_safe(A)
  D = A.sum(axis=0)
  if symmetric:
    D_negative_one_half = diags(D**(-0.5))
    P_symmetric = D_negative_one_half @ A @ D_negative_one_half
    if return_degree:
      return P_symmetric, D
    else:
      return P_symmetric
  else:
    return diags(1/D) @ A

# Cell
def diffusion_matrix_from_points(X, anisotropy = 1, k = 10, sigma = None, threshold = 1e-5, metric = 'euclidean' ):
    """Computes diffusion matrix from a data matrix, with options for type of kernel used.
    Returns a csr sparse array.

    Parameters
    ----------
    X : ndarray or sparse array
      data matrix
    anisotropy : float in [0,1], optional
      level of density correction. 1 fully renormalizes by density, by default 1
    k : int, optional
      number of neighbors to use when calculating adaptive kernel, by default 10
    sigma : float, optional
      kernel bandwidth; if specified, uses anisotropic instead of adaptive anisotropic kernel, by default None
    threshold : float, optional
      any values in the affinity matrix below this level are zeroed, by default 1e-5
    metric : str, optional
      used in distance matrix calculations, by default 'euclidean'
    """
    D = distance_matrix(X, metric = 'euclidean')
    if sigma is not None:
        A = anisotropic_kernel(D, sigma = sigma, alpha = anisotropy)
    else:
        A = adaptive_anisotropic_kernel(D, alpha = anisotropy)
    A = zero_negligible_thresholds(A, threshold=threshold)


# Cell
import scipy
import matplotlib.pyplot as plt
def diffusion_coordinates(P_symmetric, D, t = 1, plot_evals = False):
    # given symmetric diffusion matrix and density, constructs diffusion map
    Dnoh = diags(D**-0.5)
    # Decompose Ms
    eig_vals, eig_vecs = scipy.sparse.linalg.eigs(P_symmetric)
    # sort eigenvalues and eigenvectors(they are inconsistently sorted by default)
    sorted_idxs = np.argsort(eig_vals)
    eig_vals = eig_vals[sorted_idxs]
    eig_vecs = eig_vecs[:,sorted_idxs]
    # Normalize the eigenvector
    eig_psi_components = Dnoh @ eig_vecs
    eig_psi_components = eig_psi_components @ np.diag(np.power(np.linalg.norm(eig_psi_components, axis=0), -1))
    # Remove the trivial eigenvalue and eigenvector
    eig_vals = eig_vals[:-1]
    if plot_evals:
        print(eig_vals)
        fig, ax = plt.subplots()
        ax.bar([str(i) for i in range(len(eig_vals))], eig_vals**t)
        ax.set_title("Evals")
        plt.show()
    eig_psi_components = eig_psi_components[:,:-1]
    # Construct the diffusion map
    # diff_map = eig_psi_components @ np.diag(eig_vals**t)
    diff_map = eig_vals**t * eig_psi_components
    diff_map = diff_map[:,::-1]
    diff_map = diff_map
    return diff_map

# Cell
import logging
def diffusion_map_from_points(X, t = 1, kernel_type = "anisotropic", alpha = 0.5, sigma = "automatic", k = 10, plot_evals = False):
    """Creates diffusion map from data matrix X, using specified kernel.

    Parameters
    ----------
    X : ndarray, possibly sparse
      data matrix
    t : int
      steps of diffusion to take.
    kernel_type : "adaptive" or "adaptive anisotropic", optional
      Type of kernel to use, by default "anisotropic"
    alpha : float, optional
      Density normalization, between 0 and 1, by default 0.5
    sigma : float, optional
      kernel bandwidth, by default "automatic"
    k : int, optional
      nearest neighbor number to use when estimating kernel bandwidth, by default 10

    Returns
    -------
    ndarray
      new coordinates of the data in diffusion space, as the rows of this matrix, ordered by the importance of the eigenvalue
    """
    Dists = distance_matrix(X)
    if sigma == "automatic":
        # Heuristic for sigma: median of the distance to the kth nearest neighbor
        sigma = np.median(np.partition(Dists,k)[:,k])
        print("using sigma = ",sigma)
    W = anisotropic_kernel(Dists, sigma=sigma, alpha = alpha)
    P_symmetric, D = diffusion_matrix(W, symmetric=True, return_degree=True)
    diff_map = diffusion_coordinates(P_symmetric, D, t = t, plot_evals = plot_evals)
    return diff_map

# Cell
def diffusion_map_from_affinities(A, t = 1, plot_evals = False):
    # compute symmetric diffusion matrix
    P_symmetric, D = diffusion_matrix(A, symmetric=True, return_degree=True)
    # compute diffusion map
    diff_map = diffusion_coordinates(P_symmetric, D, t = t, plot_evals = plot_evals)
    return diff_map

# Cell
# For plotting 2D and 3D graphs
import plotly
import plotly.graph_objs as go
import plotly.express as px
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits import mplot3d

def plot_3d(X,distribution=None, title="",lim=None,use_plotly=False,colorbar = False, cmap="plasma"):
    if distribution is None:
        distribution = np.zeros(len(X))
    if lim is None:
        lim = np.max(np.linalg.norm(X,axis=1))
    if use_plotly:
        d = {'x':X[:,0],'y':X[:,1],'z':X[:,2],'colors':distribution}
        df = pd.DataFrame(data=d)
        fig = px.scatter_3d(df, x='x',y='y',z='z',color='colors', title=title, range_x=[-lim,lim], range_y=[-lim,lim],range_z=[-lim,lim])
        fig.show()
    else:
        fig = plt.figure(figsize=(10,10))
        ax = fig.add_subplot(111,projection='3d')
        ax.axes.set_xlim3d(left=-lim, right=lim)
        ax.axes.set_ylim3d(bottom=-lim, top=lim)
        ax.axes.set_zlim3d(bottom=-lim, top=lim)
        im = ax.scatter(X[:,0],X[:,1],X[:,2],c=distribution,cmap=cmap)
        ax.set_title(title)
        if colorbar: fig.colorbar(im, ax=ax)
        plt.show()


# Cell
def flow_neighbors(num_nodes, P_graph, n_neighbors=5):
    # remove self loop
    P_graph = P_graph - torch.eye(num_nodes).to(P_graph.device)
    # return k nearest neighbor indices
    _, neighbors = torch.topk(P_graph, n_neighbors)
    # convert to edge_index format
    row = torch.arange(num_nodes).repeat_interleave(n_neighbors).to(P_graph.device)
    col = neighbors.flatten().to(P_graph.device)
    return torch.stack((row, col))

# Cell
import torch
from torch.utils.data import Dataset
import matplotlib.pyplot as plt
import numpy as np
import umap
from sklearn.neighbors import NearestNeighbors
import torch.nn.functional as F
from .data_processing import flashlight_affinity_matrix, diffusion_map_from_affinities, flow_neighbors
class ManifoldWithVectorField(Dataset):
    """
    Dataset object to be used with FRED for pointcloud and velocity input data.
    Takes np.arrays for X (points) and velocities (velocity vectors per point).
    For each item retrieved, returns a neighborhood around that point (based on local euclidean neighbors) containing local affinities

    """
    def __init__(self, X, velocities, labels, sigma="automatic", flow_strength = 1, prior_embedding = "diffusion map", t_dmap = 1, dmap_coords_to_use = 2, n_neighbors = 5, minibatch_size = 100, nbhd_strategy = "flow neighbors", verbose = False):
        # Step 0: Convert data into tensors
        self.X = torch.tensor(X).float()
        self.velocities = torch.tensor(velocities).float()
        self.labels = labels
        self.n_neighbors = n_neighbors
        self.nbhd_strategy = nbhd_strategy
        self.n_nodes = self.X.shape[0]
        self.minibatch_size = minibatch_size

        # Step 1. Build graph on input data, using flashlight kernel
        if verbose: print("Building flow affinitiy matrix")
        self.A = flashlight_affinity_matrix(self.X, self.velocities, sigma = sigma, flow_strength = flow_strength)
        self.P_graph = F.normalize(self.A, p=1, dim=1)
        # visualize affinity matrix
        plt.imshow(self.A.numpy())

        # Step 2. Take a diffusion map of the data
        # These will become our 'precomputed distances' which we use to regularize the embedding
        if prior_embedding == "diffusion map":
            self.P_graph_symmetrized = self.P_graph + self.P_graph.T
            diff_map = diffusion_map_from_affinities(
                self.P_graph_symmetrized, t=t_dmap, plot_evals=False
            )
            self.diff_coords = diff_map[:, :dmap_coords_to_use]
            self.diff_coords = self.diff_coords.real
            self.diff_coords = torch.tensor(self.diff_coords.copy()).float()
            self.precomputed_distances = torch.cdist(self.diff_coords, self.diff_coords)
            # scale distances between 0 and 1
            self.precomputed_distances = 2 * (
                self.precomputed_distances / torch.max(self.precomputed_distances)
            )
            self.precomputed_distances = (
                self.precomputed_distances.detach()
            )  # no need to have gradients from this operation
        elif prior_embedding == "UMAP":
            print("Computing UMAP")
            reducer = umap.UMAP()
            self.umap_coords = torch.tensor(reducer.fit_transform(self.X))
            self.precomputed_distances = torch.cdist(self.umap_coords, self.umap_coords)
        else:
            raise ValueError("Prior embedding must be either 'diffusion map' or 'UMAP'")
        # Step 3: This returns a sparse representation of the flow neighborhoods, in the form of two tensors: row, col. The numbers in row specify the index, and the adjacent entries in col are the neighbors of that index.
        if nbhd_strategy == "flow neighbors":
            self.neighborhoods = flow_neighbors(self.n_nodes, self.P_graph, self.n_neighbors)
        if nbhd_strategy == "euclidean neighbors":
            # Get points with nearest diffusion distances, based on above computation with dmap on symmetrized
            # directed diffusion matrix
            Neighbors = NearestNeighbors(n_neighbors=self.n_neighbors).fit(self.X)
            dists, indxs = Neighbors.kneighbors()
            self.neighborhoods = torch.tensor(indxs)
    def neighbors_from_point(self, idx):
        if self.nbhd_strategy == "flow neighbors":
            # Returns list of idxs of neighbors of the given idx
            row, col = self.neighborhoods
            idxs = torch.squeeze(torch.nonzero(row == idx))
            return col[idxs]
        elif self.nbhd_strategy == "euclidean neighbors":
            return self.neighborhoods[idx]

    def __len__(self):
        return len(self.X)
    def __getitem__(self, idx):
        # Get the neighborhood around the central point
        nbhd_idxs = self.neighbors_from_point(idx)
        # And sample random points -- for negative sampling loss
        random_idxs = torch.tensor(np.random.choice(np.arange(self.n_nodes), size=(self.minibatch_size))).long()
        minibatch_idxs = torch.concat([torch.tensor([idx]), nbhd_idxs, random_idxs])
        # Compute miniature diffusion matrix
        A_batch = self.A[minibatch_idxs][:,minibatch_idxs]
        P_batch = F.normalize(A_batch, p=1, dim=1)
        # Get actual points
        X_batch = self.X[minibatch_idxs]
        # Get subset of distances
        mini_precomputed_distances = self.precomputed_distances[minibatch_idxs][:,minibatch_idxs]
        # compute sparse representation of neighborhood around idx
        row = torch.zeros(self.n_neighbors).long()
        col = torch.arange(1,self.n_neighbors+1).long()
        neighbors = torch.vstack(
            [row, col]
        )
        # Embed these into a dictionary for easy cross reference
        return_dict = {
            "P":P_batch,
            "X":X_batch,
            "num flow neighbors":self.n_neighbors,
            "precomputed distances": mini_precomputed_distances,
            "neighbors":neighbors,
            "labels":self.labels[minibatch_idxs],
        }
        return return_dict
    def all_data(self):
        return_dict = {
            "P":self.P_graph,
            "X":self.X,
            "num flow neighbors":self.n_neighbors,
            "precomputed distances":self.precomputed_distances,
            "neighbors": self.neighborhood,
        }
        return return_dict

# Cell
from torch.utils.data import DataLoader
def dataloader_from_ndarray(X, flow, labels):
    ds = ManifoldWithVectorField(X, flow, labels)
    dataloader = DataLoader(ds, batch_size=None, shuffle=True)
    return dataloader
# AUTOGENERATED! DO NOT EDIT! File to edit: 01c Plotting Utils.ipynb (unless otherwise specified).

__all__ = ['xy_tilt', 'add_noise', 'directed_circle', 'directed_spiral', 'directed_spiral_uniform',
           'directed_spiral_delayed', 'generate_prism', 'directed_cylinder', 'directed_swiss_roll',
           'directed_swiss_roll_uniform', 'directed_swiss_roll_delayed', 'directed_one_variable_function',
           'directed_sine', 'directed_sine_ribbon', 'directed_sinh', 'directed_sinh_branch', 'directed_sine_moons',
           'angle_x', 'whirlpool', 'rejection_sample_for_torus', 'directed_torus', 'directed_sphere',
           'rnavelo_find_cluster_key', 'rnavelo_add_labels', 'rnavelo_preprocess', 'rnavelo', 'rnavelo_pcs',
           'rnavelo_plot_pca', 'plot_directed_2d', 'plot_origin_3d', 'plot_directed_3d', 'plot_3d',
           'visualize_edge_index', 'display_galary', 'display_flow_galary']

# Cell
# Tilt 2d plane into 3d space
import numpy as np
def xy_tilt(X, flows, xtilt=0, ytilt=0):
    xrotate = np.array([[1,              0,             0],
                        [0,  np.cos(xtilt), np.sin(xtilt)],
                        [0, -np.sin(xtilt), np.cos(xtilt)]])
    yrotate = np.array([[np.cos(ytilt), 0, -np.sin(ytilt)],
                        [            0, 1,              0],
                        [np.sin(ytilt), 0,  np.cos(ytilt)]])
    X = X @ xrotate @ yrotate
    flows = flows @ xrotate @ yrotate
    return X, flows

# Cell
def add_noise(X, sigma=0):
    return X + np.random.normal(0, sigma, X.shape)

# Cell
def directed_circle(num_nodes=500, radius=1, xtilt=0, ytilt=0, sigma=0, inverse=False):
    """
    Sample `n` data points on a circle.
    In addition to the points, returns a "flow" vector at each point.

    Parameters
    -----------
    num_nodes : int, default=500
        Number of data points in shape.
    radius : float, default=1
        Radius of circle.

    xtilt : float, default=0
        Angle to rotate around the x-axis.
    ytilt : float, default=0
        Angle to rotate around the y-axis.
    sigma : float, default=0
        Amount of gaussian noise
    inverse : bool, default=False
        Whether to flip the direction of flow
    """
    # sample random angles between 0 and 2pi
    thetas = np.random.uniform(0, 2*np.pi, num_nodes)
    thetas = np.sort(thetas)
    labels = thetas
    # calculate x and y coordinates
    x = np.cos(thetas) * radius
    y = np.sin(thetas) * radius
    z = np.zeros(num_nodes)
    X = np.column_stack((x, y, z))
    # calculate the angle of the tangent
    alphas = thetas + np.pi/2
    # calculate the coordinates of the tangent
    u = np.cos(alphas)
    v = np.sin(alphas)
    w = np.zeros(num_nodes)
    flows = np.column_stack((u, v, w))
    flows = -flows if inverse else flows
    # tilt and add noise
    X, flows = xy_tilt(X, flows, xtilt, ytilt)
    X = add_noise(X, sigma)
    return X, flows, labels

# Cell
def directed_spiral(num_nodes=500, num_spirals=1.5, radius=1, xtilt=0, ytilt=0, sigma=0, inverse=False):
    """
    Sample `n` data points on a spiral.
    In addition to the points, returns a "flow" vector at each point.

    Parameters
    -----------
    num_nodes : int, default=500
        Number of data points in shape.
    num_spirals : float, default=1.5
        Number of revolution.
    radius : float, default=1
        Radius of spiral.

    xtilt : float, default=0
        Angle to rotate around the x-axis.
    ytilt : float, default=0
        Angle to rotate around the y-axis.
    sigma : float, default=0
        Amount of gaussian noise
    inverse : bool, default=False
        Whether to flip the direction of flow
    """
    # sample random angles between 0 and num_spirals * 2pi
    thetas = np.random.uniform(0, num_spirals*2*np.pi, num_nodes)
    thetas = np.sort(thetas)
    labels = thetas
    # calculate x and y coordinates
    x = np.cos(thetas) * thetas * radius
    y = np.sin(thetas) * thetas * radius
    z = np.zeros(num_nodes)
    X = np.column_stack((x, y, z))
    # calculate the angle of the tangent
    alphas = thetas + np.pi/2
    # calculate the coordinates of the tangent
    u = np.cos(alphas) * thetas
    v = np.sin(alphas) * thetas
    w = np.zeros(num_nodes)
    flows = np.column_stack((u, v, w))
    flows = -flows if inverse else flows
    # tilt and add noise
    X, flows = xy_tilt(X, flows, xtilt, ytilt)
    X = add_noise(X, sigma)
    return X, flows, labels

# Cell
def directed_spiral_uniform(num_nodes=500, num_spirals=1.5, radius=1, xtilt=0, ytilt=0, sigma=0, inverse=False):
    """
    Sample `n` data points on a spiral.
    In addition to the points, returns a "flow" vector at each point.

    Parameters
    -----------
    num_nodes : int, default=500
        Number of data points in shape.
    num_spirals : float, default=1.5
        Number of revolution.
    radius : float, default=1
        Radius of spiral.

    xtilt : float, default=0
        Angle to rotate around the x-axis.
    ytilt : float, default=0
        Angle to rotate around the y-axis.
    sigma : float, default=0
        Amount of gaussian noise
    inverse : bool, default=False
        Whether to flip the direction of flow
    """
    # sample random angles between 0 and num_spirals * 2pi
    t1 = np.random.uniform(0, num_spirals*2*np.pi, num_nodes)
    t2 = np.random.uniform(0, num_spirals*2*np.pi, num_nodes)
    thetas = np.maximum(t1, t2)
    thetas = np.sort(thetas)
    labels = thetas
    # calculate x and y coordinates
    x = np.cos(thetas) * thetas * radius
    y = np.sin(thetas) * thetas * radius
    z = np.zeros(num_nodes)
    X = np.column_stack((x, y, z))
    # calculate the angle of the tangent
    alphas = thetas + np.pi/2
    # calculate the coordinates of the tangent
    u = np.cos(alphas)
    v = np.sin(alphas)
    w = np.zeros(num_nodes)
    flows = np.column_stack((u, v, w))
    flows = -flows if inverse else flows
    # tilt and add noise
    X, flows = xy_tilt(X, flows, xtilt, ytilt)
    X = add_noise(X, sigma)
    return X, flows, labels

# Cell
def directed_spiral_delayed(num_nodes=500, num_spirals=1.5, radius=1, xtilt=0, ytilt=0, sigma=0, inverse=False):
    """
    Sample `n` data points on a spiral.
    In addition to the points, returns a "flow" vector at each point.

    Parameters
    -----------
    num_nodes : int, default=500
        Number of data points in shape.
    num_spirals : float, default=1.5
        Number of revolution.
    radius : float, default=1
        Radius of spiral.

    xtilt : float, default=0
        Angle to rotate around the x-axis.
    ytilt : float, default=0
        Angle to rotate around the y-axis.
    sigma : float, default=0
        Amount of gaussian noise
    inverse : bool, default=False
        Whether to flip the direction of flow
    """
    # sample random angles between 0 and num_spirals * 2pi
    thetas = np.random.uniform(num_spirals*np.pi, num_spirals*3*np.pi, num_nodes)
    thetas = np.sort(thetas)
    labels = thetas
    # calculate x and y coordinates
    x = np.cos(thetas) * thetas * radius
    y = np.sin(thetas) * thetas * radius
    z = np.zeros(num_nodes)
    X = np.column_stack((x, y, z))
    # calculate the angle of the tangent
    alphas = thetas + np.pi/2
    # calculate the coordinates of the tangent
    u = np.cos(alphas) * thetas
    v = np.sin(alphas) * thetas
    w = np.zeros(num_nodes)
    flows = np.column_stack((u, v, w))
    flows = -flows if inverse else flows
    # tilt and add noise
    X, flows = xy_tilt(X, flows, xtilt, ytilt)
    X = add_noise(X, sigma)
    return X, flows, labels

# Cell
def generate_prism(num_nodes, X, height=20):
    z_noise = np.random.uniform(-height/2, height/2, num_nodes)
    X[:,2] = X[:,2] + z_noise
    return X

# Cell
def directed_cylinder(num_nodes=1000, height=20, radius=1, xtilt=0, ytilt=0, sigma=0, inverse=False):
    """
    Sample `n` data points on a cylinder.
    In addition to the points, returns a "flow" vector at each point.

    Parameters
    -----------
    num_nodes : int, default=1000
        Number of data points in shape.
    radius : float, default=1
        Radius of cylinder.
    height : float, default=20
        Height of cylinder.

    xtilt : float, default=0
        Angle to rotate around the x-axis.
    ytilt : float, default=0
        Angle to rotate around the y-axis.
    sigma : float, default=0
        Amount of gaussian noise
    inverse : bool, default=False
        Whether to flip the direction of flow
    """
    X, flows, labels = directed_circle(num_nodes, radius, xtilt, ytilt, sigma, inverse)
    X = generate_prism(num_nodes, X, height)
    return X, flows, labels

# Cell
def directed_swiss_roll(num_nodes=1000, num_spirals=1.5, height=20, radius=1, xtilt=0, ytilt=0, sigma=0, inverse=False):
    """
    Sample `n` data points on a swiss roll.
    In addition to the points, returns a "flow" vector at each point.

    Parameters
    -----------
    num_nodes : int, default=1000
        Number of data points in shape.
    num_spirals : float, default=1.5
        Number of revolution.
    height : float, default=20
        Height of swiss roll.
    radius : float, default=1
        Radius of swiss roll.

    xtilt : float, default=0
        Angle to rotate around the x-axis.
    ytilt : float, default=0
        Angle to rotate around the y-axis.
    sigma : float, default=0
        Amount of gaussian noise
    inverse : bool, default=False
        Whether to flip the direction of flow
    """
    X, flows, labels = directed_spiral(num_nodes, num_spirals, radius, xtilt, ytilt, sigma, inverse)
    X = generate_prism(num_nodes, X, height)
    return X, flows, labels

# Cell
def directed_swiss_roll_uniform(num_nodes=1000, num_spirals=1.5, height=20, radius=1, xtilt=0, ytilt=0, sigma=0, inverse=False):
    """
    Sample `n` data points on a swiss roll.
    In addition to the points, returns a "flow" vector at each point.

    Parameters
    -----------
    num_nodes : int, default=1000
        Number of data points in shape.
    num_spirals : float, default=1.5
        Number of revolution.
    height : float, default=20
        Height of swiss roll.
    radius : float, default=1
        Radius of swiss roll.

    xtilt : float, default=0
        Angle to rotate around the x-axis.
    ytilt : float, default=0
        Angle to rotate around the y-axis.
    sigma : float, default=0
        Amount of gaussian noise
    inverse : bool, default=False
        Whether to flip the direction of flow
    """
    X, flows, labels = directed_spiral_uniform(num_nodes, num_spirals, radius, xtilt, ytilt, sigma, inverse)
    X = generate_prism(num_nodes, X, height)
    return X, flows, labels

# Cell
def directed_swiss_roll_delayed(num_nodes=1000, num_spirals=1.5, height=20, radius=1, xtilt=0, ytilt=0, sigma=0, inverse=False):
    """
    Sample `n` data points on a swiss roll.
    In addition to the points, returns a "flow" vector at each point.

    Parameters
    -----------
    num_nodes : int, default=1000
        Number of data points in shape.
    num_spirals : float, default=1.5
        Number of revolution.
    height : float, default=20
        Height of swiss roll.
    radius : float, default=1
        Radius of swiss roll.

    xtilt : float, default=0
        Angle to rotate around the x-axis.
    ytilt : float, default=0
        Angle to rotate around the y-axis.
    sigma : float, default=0
        Amount of gaussian noise
    inverse : bool, default=False
        Whether to flip the direction of flow
    """
    X, flows, labels = directed_spiral_delayed(num_nodes, num_spirals, radius, xtilt, ytilt, sigma, inverse)
    X = generate_prism(num_nodes, X, height)
    return X, flows, labels

# Cell
def directed_one_variable_function(func, deriv, xlow, xhigh, num_nodes=100, xtilt=0, ytilt=0, sigma=0, inverse=False):
    """
    Sample data points along a one variable function.
    In addition to the points, returns a "flow" vector at each point.

    Parameters
    -----------
    func : function, y = func(x)
        An one variable function
    deriv : function, y' = deriv(x)
        The derivative of func
    xlow : float
        Lower bound of x
    xlow : float
        Upper bound of x
    num_nodes : int, default=100
        Number of data points in shape.

    xtilt : float, default=0
        Angle to rotate around the x-axis.
    ytilt : float, default=0
        Angle to rotate around the y-axis.
    sigma : float, default=0
        Amount of gaussian noise
    inverse : bool, default=False
        Whether to flip the direction of flow
    """
    # positions
    x = np.random.uniform(xlow, xhigh, num_nodes)
    x = np.sort(x)
    y = func(x)
    z = np.zeros(num_nodes)
    X = np.column_stack((x, y, z))
    labels = x
    # vectors
    u = np.ones(num_nodes)
    v = deriv(x)
    w = np.zeros(num_nodes)
    flows = np.column_stack((u, v, w))
    flows = -flows if inverse else flows
    # tilt and add noise
    X, flows = xy_tilt(X, flows, xtilt, ytilt)
    X = add_noise(X, sigma)
    return X, flows, labels

# Cell
def directed_sine(num_nodes=500, xscale=1, yscale=1, xlow=-2*np.pi, xhigh=2*np.pi, xtilt=0, ytilt=0, sigma=0, inverse=False):
    """
    Sample data points along a sine function.
    In addition to the points, returns a "flow" vector at each point.

    Parameters
    -----------
    num_nodes : int, default=500
        Number of data points in shape.
    xscale : float, default=1
        Factor to stretch the x-axis
    yscale : float, default=1
        Factor to stretch the y-axis
    xlow : float, default=-2*pi
        Lower bound of x
    xlow : float, default=2*pi
        Upper bound of x

    xtilt : float, default=0
        Angle to rotate around the x-axis.
    ytilt : float, default=0
        Angle to rotate around the y-axis.
    sigma : float, default=0
        Amount of gaussian noise
    inverse : bool, default=False
        Whether to flip the direction of flow
    """
    X, flows, labels = directed_one_variable_function(
        lambda x: np.sin(x / xscale) * yscale,
        lambda x: np.cos(x / xscale) / xscale * yscale,
        xlow, xhigh,
        num_nodes, xtilt, ytilt, sigma, inverse
    )
    return X, flows, labels

# Cell
def directed_sine_ribbon(num_nodes=1000, xscale=1, yscale=1, xlow=-2*np.pi, xhigh=2*np.pi, height=20, xtilt=0, ytilt=0, sigma=0, inverse=False):
    """
    Sample data points along a sine function with height.
    In addition to the points, returns a "flow" vector at each point.

    Parameters
    -----------
    num_nodes : int, default=1000
        Number of data points in shape.
    xscale : float, default=1
        Factor to stretch the x-axis
    yscale : float, default=1
        Factor to stretch the y-axis
    xlow : float, default=-2*pi
        Lower bound of x
    xlow : float, default=2*pi
        Upper bound of x
    height : float, default=20
        Height of the ribbon

    xtilt : float, default=0
        Angle to rotate around the x-axis.
    ytilt : float, default=0
        Angle to rotate around the y-axis.
    sigma : float, default=0
        Amount of gaussian noise
    inverse : bool, default=False
        Whether to flip the direction of flow
    """
    X, flows, labels = directed_sine(num_nodes, xscale, yscale, xlow, xhigh, xtilt, ytilt, sigma, inverse)
    X = generate_prism(num_nodes, X, height)
    return X, flows, labels

# Cell
def directed_sinh(num_nodes=500, xscale=1, yscale=1, xlow=-2*np.pi, xhigh=2*np.pi, xtilt=0, ytilt=0, sigma=0, inverse=False):
    """
    Sample data points along a sinh function.
    In addition to the points, returns a "flow" vector at each point.

    Parameters
    -----------
    num_nodes : int, default=500
        Number of data points in shape.
    xscale : float, default=1
        Factor to stretch the x-axis
    yscale : float, default=1
        Factor to stretch the y-axis
    xlow : float, default=-2*pi
        Lower bound of x
    xlow : float, default=2*pi
        Upper bound of x

    xtilt : float, default=0
        Angle to rotate around the x-axis.
    ytilt : float, default=0
        Angle to rotate around the y-axis.
    sigma : float, default=0
        Amount of gaussian noise
    inverse : bool, default=False
        Whether to flip the direction of flow
    """
    X, flows, labels = directed_one_variable_function(
        lambda x: np.sinh(x / xscale) * yscale,
        lambda x: np.cosh(x / xscale) / xscale * yscale,
        xlow, xhigh,
        num_nodes, xtilt, ytilt, sigma, inverse
    )
    return X, flows, labels

# Cell
def directed_sinh_branch(num_nodes=1000, xscale=1, yscale=1, xtilt=0, ytilt=0, sigma=0, inverse=False):
    """
    Sample data points along a sinh-sine branch.
    In addition to the points, returns a "flow" vector at each point.

    Parameters
    -----------
    num_nodes : int, default=1000
        Number of data points in shape.
    xscale : float, default=1
        Factor to stretch the x-axis
    yscale : float, default=1
        Factor to stretch the y-axis

    xtilt : float, default=0
        Angle to rotate around the x-axis.
    ytilt : float, default=0
        Angle to rotate around the y-axis.
    sigma : float, default=0
        Amount of gaussian noise
    inverse : bool, default=False
        Whether to flip the direction of flow
    """
    num_nodes_per_branch = num_nodes//3
    X_root, flows_root, labels_root = directed_sinh(num_nodes-2*num_nodes_per_branch, xscale, yscale, -xscale*np.pi*0.84, 0, xtilt, ytilt, sigma, inverse)
    X_branch1, flows_branch1, labels_branch1 = directed_sinh(num_nodes_per_branch, xscale, yscale, 0, xscale*np.pi*0.84, xtilt, ytilt, sigma, inverse)
    X_branch2, flows_branch2, labels_branch2 = directed_sine(num_nodes_per_branch, xscale, yscale, 0, xscale*np.pi*2, xtilt, ytilt, sigma, inverse)
    # concatenate
    X = np.concatenate((X_root, X_branch1, X_branch2))
    flows = np.concatenate((flows_root, flows_branch1, flows_branch2))
    labels = np.concatenate((labels_root - np.pi*3, labels_branch1, labels_branch2 + np.pi*3))
    return X, flows, labels


# Cell
def directed_sine_moons(num_nodes=500, xscale=1, yscale=1, xtilt=0, ytilt=0, sigma=0, inverse=False):
    """
    Sample data points along two sine moons.
    In addition to the points, returns a "flow" vector at each point.

    Parameters
    -----------
    num_nodes : int, default=500
        Number of data points in shape.
    xscale : float, default=1
        Factor to stretch the x-axis
    yscale : float, default=1
        Factor to stretch the y-axis

    xtilt : float, default=0
        Angle to rotate around the x-axis.
    ytilt : float, default=0
        Angle to rotate around the y-axis.
    sigma : float, default=0
        Amount of gaussian noise
    inverse : bool, default=False
        Whether to flip the direction of flow
    """
    num_nodes_per_moon = num_nodes // 2
    X_moon1, flows_moon1, labels_moon1 = directed_sine(num_nodes_per_moon, xscale, yscale, 0, xscale*np.pi, xtilt, ytilt, sigma, inverse)
    X_moon2, flows_moon2, labels_moon2 = X, flows, labels = directed_one_variable_function(
        lambda x: np.cos(x / xscale) * yscale + 0.3,
        lambda x: -np.sin(x / xscale) / xscale * yscale,
        xscale*np.pi/2, xscale*np.pi*3/2,
        num_nodes_per_moon, xtilt, ytilt, sigma, inverse
    )
    # concatenate
    X = np.concatenate((X_moon1, X_moon2))
    flows = np.concatenate((flows_moon1, flows_moon2))
    labels = np.concatenate((labels_moon1 - np.pi, labels_moon2))
    return X, flows, labels

# Cell
def angle_x(X):
    """Returns angle in [0, 2pi] corresponding to each point X"""
    X_complex = X[:,0] + np.array([1j])*X[:,1]
    return np.angle(X_complex)

# Cell
def whirlpool(X):
    """Generates a whirlpool for flow assignment. Works in both 2d and 3d space.

    Parameters
    ----------
    X : ndarray
        input data, 2d or 3d
    """
    # convert X into angles theta, where 0,0 is 0, and 0,1 is pi/2
    X_angles = angle_x(X)
    # create flows
    flow_x = np.sin(2*np.pi - X_angles)
    flow_y = np.cos(2*np.pi - X_angles)
    output = np.column_stack([flow_x,flow_y])
    if X.shape[1] == 3:
        # data is 3d
        flow_z = np.zeros(X.shape[0])
        output = np.column_stack([output,flow_z])
    return output

# Cell
def rejection_sample_for_torus(n, r, R):
    # Rejection sampling torus method [Sampling from a torus (Revolutions)](https://blog.revolutionanalytics.com/2014/02/sampling-from-a-torus.html)
    xvec = np.random.random(n) * 2 * np.pi
    yvec = np.random.random(n) * (1/np.pi)
    fx = (1 + (r/R)*np.cos(xvec)) / (2*np.pi)
    return xvec[yvec < fx]

def directed_torus(n=2000, c=2, a=1, flow_type = 'whirlpool', noise=None, seed=None, use_guide_points = False):
    """
    Sample `n` data points on a torus. Modified from [tadasets.shapes — TaDAsets 0.1.0 documentation](https://tadasets.scikit-tda.org/en/latest/_modules/tadasets/shapes.html#torus)
    Uses rejection sampling.

    In addition to the points, returns a "flow" vector at each point.

    Parameters
    -----------
    n : int
        Number of data points in shape.
    c : float
        Distance from center to center of tube.
    a : float
        Radius of tube.
    flow_type, in ['whirlpool']

    noise : float, default=None
        Amount of noise
    seed : int, default=None
        Seed for random state.
    """

    assert a <= c, "That's not a torus"

    np.random.seed(seed)
    theta = rejection_sample_for_torus(n-2, a, c)
    phi = np.random.random((len(theta))) * 2.0 * np.pi

    X = np.zeros((len(theta), 3))
    X[:, 0] = (c + a * np.cos(theta)) * np.cos(phi)
    X[:, 1] = (c + a * np.cos(theta)) * np.sin(phi)
    X[:, 2] = a * np.sin(theta)

    if use_guide_points:
        X = np.vstack([[[0,-c-a,0],[0,c-a,0],[0,c,a]],X])

    if noise:
        X += noise * np.random.randn(*X.shape)

    if flow_type == 'whirlpool':
        flows = whirlpool(X)
    else:
        raise NotImplementedError

    return X, flows, phi

# Cell
import tadasets
def directed_sphere(n=2000, r=1, flow_type = 'whirlpool', noise=None):
    """
    Sample `n` data points on a sphere.
    In addition to the points, returns a "flow" vector at each point.

    Parameters
    -----------
    n : int
        Number of data points in shape.
    r : float
        Radius of sphere.
    flow_type, in ['whirlpool']

    noise : float, default=None
        Amount of noise
    seed : int, default=None
        Seed for random state.
    """
    X = tadasets.sphere(n, r, noise)
    labels = angle_x(X)
    if flow_type == 'whirlpool':
        flows = whirlpool(X)
    else:
        raise NotImplementedError
    return X, flows, labels

# Cell

import scvelo as scv
import torch

def rnavelo_find_cluster_key(adata):
    obs_keys = adata.obs.keys()
    possible_keys = ["clusters", "celltype", "Clusters", "true_t"]
    for key in possible_keys:
        if key in obs_keys:
            return key
    return None

def rnavelo_add_labels(adata):
    cluster_key = rnavelo_find_cluster_key(adata)
    if cluster_key in ["clusters", "celltype"]:
        clusters = adata.obs[cluster_key]
        cluster_set = set(clusters)
        d = {cluster: i for i, cluster in enumerate(cluster_set)}
        labels = torch.tensor([d[cluster] for cluster in clusters])

    elif cluster_key in ["Clusters", "true_t"]:
        labels = torch.tensor(adata.obs[cluster_key])

    return labels

def rnavelo_preprocess(adata):
    #preprocess data and calculate rna velocity
    scv.pp.filter_and_normalize(adata)
    scv.pp.moments(adata)
    scv.tl.velocity(adata, mode='stochastic')


def rnavelo(adata):
    rnavelo_preprocess(adata)

    X = torch.tensor(adata.X) if type(adata.X) is np.ndarray else torch.tensor(adata.X.todense())
    flows = torch.tensor(adata.layers["velocity"])
    labels = rnavelo_add_labels(adata)

    return X, flows, labels

def rnavelo_pcs(adata):
    rnavelo_preprocess(adata)

    # calculate pca embedding
    if not(hasattr(adata, "obsm") and "X_pca" in adata.obsm.keys()):
        scv.pp.pca(adata)

    # calculate velocity pca and display pca plot (2 dimensions)
    scv.tl.velocity_graph(adata)
    scv.tl.velocity_embedding(adata, basis='pca', direct_pca_projection=False)

    X = torch.tensor(adata.obsm["X_pca"].copy())
    flows = torch.tensor(adata.obsm["velocity_pca"].copy())
    labels = rnavelo_add_labels(adata)
    n_pcs = X.shape[1]

    return X, flows, labels, n_pcs

def rnavelo_plot_pca(adata):
    rnavelo_pcs(adata)
    cluster_key = rnavelo_find_cluster_key(adata)
    scv.pl.velocity_embedding_stream(adata, basis='pca', color=cluster_key)

# Cell
import matplotlib.pyplot as plt


def plot_directed_2d(X, flows, labels=None, mask_prob=0.5, cmap="viridis", ax=None):
    num_nodes = X.shape[0]
    alpha_points, alpha_arrows = (0.1, 1) if labels is None else (1, 0.1)
    if ax is None:
        fig = plt.figure()
        ax = fig.add_subplot()
    ax.scatter(X[:, 0], X[:, 1], marker=".", c=labels, cmap=cmap, alpha=alpha_points)
    mask = np.random.rand(num_nodes) > mask_prob
    ax.quiver(X[mask, 0], X[mask, 1], flows[mask, 0], flows[mask, 1], alpha=alpha_arrows)
    ax.set_aspect("equal")
    if ax is None:
        plt.show()


# Cell
def plot_origin_3d(ax, xlim, ylim, zlim):
    ax.plot(xlim, [0, 0], [0, 0], color="k", alpha=0.5)
    ax.plot([0, 0], ylim, [0, 0], color="k", alpha=0.5)
    ax.plot([0, 0], [0, 0], zlim, color="k", alpha=0.5)


def plot_directed_3d(X, flow, labels=None, mask_prob=0.5, cmap="viridis", origin=False, ax=None):
    num_nodes = X.shape[0]
    alpha_points, alpha_arrows = (0.1, 1) if labels is None else (1, 0.1)
    mask = np.random.rand(num_nodes) > mask_prob
    if ax is None:
        fig = plt.figure()
        ax = fig.add_subplot(projection="3d")
    if origin:
        plot_origin_3d(
            ax,
            xlim=[X[:, 0].min(), X[:, 0].max()],
            ylim=[X[:, 1].min(), X[:, 1].max()],
            zlim=[X[:, 2].min(), X[:, 2].max()],
        )
    ax.scatter(X[:, 0], X[:, 1], X[:, 2], marker=".", c=labels, cmap=cmap, alpha=alpha_points)
    ax.quiver(
        X[mask, 0],
        X[mask, 1],
        X[mask, 2],
        flow[mask, 0],
        flow[mask, 1],
        flow[mask, 2],
        alpha=alpha_arrows,
        length=0.5,
    )
    if ax is None:
        plt.show()


# Cell
# For plotting 2D and 3D graphs
import plotly.express as px
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


def plot_3d(
    X,
    distribution=None,
    title="",
    lim=None,
    use_plotly=False,
    colorbar=False,
    cmap="viridis",
):
    if distribution is None:
        distribution = np.zeros(len(X))
    if lim is None:
        lim = np.max(np.linalg.norm(X, axis=1))
    if use_plotly:
        d = {"x": X[:, 0], "y": X[:, 1], "z": X[:, 2], "colors": distribution}
        df = pd.DataFrame(data=d)
        fig = px.scatter_3d(
            df,
            x="x",
            y="y",
            z="z",
            color="colors",
            title=title,
            range_x=[-lim, lim],
            range_y=[-lim, lim],
            range_z=[-lim, lim],
        )
        fig.show()
    else:
        fig = plt.figure(figsize=(10, 10))
        ax = fig.add_subplot(111, projection="3d")
        ax.axes.set_xlim3d(left=-lim, right=lim)
        ax.axes.set_ylim3d(bottom=-lim, top=lim)
        ax.axes.set_zlim3d(bottom=-lim, top=lim)
        im = ax.scatter(X[:, 0], X[:, 1], X[:, 2], c=distribution, cmap=cmap)
        ax.set_title(title)
        if colorbar:
            fig.colorbar(im, ax=ax)
        plt.show()


# Cell
def visualize_edge_index(edge_index, order_ind=None, cmap = "copper", ax=None):
    num_nodes = edge_index.max() + 1
    row, col = edge_index
    dense_adj = np.zeros((num_nodes, num_nodes))
    for r, c in zip(row, col):
        dense_adj[r,c] = 1
    if order_ind is not None:
        dense_adj = dense_adj[order_ind, :][:, order_ind]
    if ax is not None:
        ax.imshow(dense_adj, cmap=cmap)
    else:
        plt.imshow(dense_adj, cmap=cmap)
        plt.show()

# Cell
import matplotlib.pyplot as plt
def display_galary(vizset, ncol=4):
    nviz = len(vizset)
    nrow = int(np.ceil(nviz/ncol))
    fig = plt.figure(figsize=(4*ncol, 3*nrow))
    for i, viz in enumerate(vizset):
        name, data, vizcall, is3d = viz
        ax = fig.add_subplot(nrow, ncol, i+1, projection="3d" if is3d else None)
        vizcall(data, ax)
        ax.set_title(name, y=1.0)

# Cell
def display_flow_galary(dataset, ncol=4):
    vizset = []
    for name, data in dataset:
        vizset.append((name, data, lambda data, ax: plot_directed_3d(
            data[0], data[1], data[2], mask_prob=0.5, ax=ax
        ), True))
    display_galary(vizset, ncol)
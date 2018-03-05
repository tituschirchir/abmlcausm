from __future__ import division

import networkx as nx


def _process_params(G, center, dim):
    import numpy as np

    if not isinstance(G, nx.Graph):
        empty_graph = nx.Graph()
        empty_graph.add_nodes_from(G)
        G = empty_graph

    if center is None:
        center = np.zeros(dim)
    else:
        center = np.asarray(center)

    if len(center) != dim:
        msg = "length of center coordinates must match dimension of layout"
        raise ValueError(msg)

    return G, center


def is_iterator(obj):
    has_next_attr = hasattr(obj, '__next__') or hasattr(obj, 'next')
    return iter(obj) is obj and has_next_attr


def arbitrary_element(iterable):
    if is_iterator(iterable):
        raise ValueError('cannot return an arbitrary item from an iterator')
    # Another possible implementation is ``for x in iterable: return x``.
    return next(iter(iterable))


def single_source_dijkstra_path_length(G, source, cutoff=None, weight='weight'):
    return multi_source_dijkstra_path_length(G, {source}, cutoff=cutoff,
                                             weight=weight)


def multi_source_dijkstra_path_length(G, sources, cutoff=None, weight='weight'):
    if not sources:
        raise ValueError('sources must not be empty')
    weight = _weight_function(G, weight)
    return _dijkstra_multisource(G, sources, weight, cutoff=cutoff)


def all_pairs_dijkstra_path_length(G, cutoff=None, weight='weight'):
    length = single_source_dijkstra_path_length
    for n in G:
        yield (n, length(G, n, cutoff=cutoff, weight=weight))


def shortest_path_length(G, source=None, target=None, weight=None):
    if source is None:
        if target is None:
            # Find paths between all pairs.
            if weight is None:
                paths = nx.all_pairs_shortest_path_length(G)
            else:
                paths = all_pairs_dijkstra_path_length(G, weight=weight)
        else:
            # Find paths from all nodes co-accessible to the target.
            with nx.utils.reversed(G):
                if weight is None:
                    # We need to exhaust the iterator as Graph needs
                    # to be reversed.
                    path_length = nx.single_source_shortest_path_length
                    paths = path_length(G, target)
                else:
                    path_length = nx.single_source_dijkstra_path_length
                    paths = path_length(G, target, weight=weight)
    else:
        if source not in G:
            raise nx.NodeNotFound("Source {} not in G".format(source))

        if target is None:
            # Find paths to all nodes accessible from the source.
            if weight is None:
                paths = nx.single_source_shortest_path_length(G, source)
            else:
                paths = nx.single_source_dijkstra_path_length(G, source,
                                                              weight=weight)
        else:
            # Find shortest source-target path.
            if weight is None:
                p = nx.bidirectional_shortest_path(G, source, target)
                paths = len(p) - 1
            else:
                paths = nx.dijkstra_path_length(G, source, target, weight)
    return paths


def random_layout(G, center=None, dim=2, random_state=None):
    import numpy as np

    G, center = _process_params(G, center, dim)
    shape = (len(G), dim)
    pos = random_state.rand(*shape) + center
    pos = pos.astype(np.float32)
    pos = dict(zip(G, pos))

    return pos


def circular_layout(G, scale=1, center=None, dim=2):
    import numpy as np

    G, center = _process_params(G, center, dim)

    paddims = max(0, (dim - 2))

    if len(G) == 0:
        pos = {}
    elif len(G) == 1:
        pos = {arbitrary_element(G): center}
    else:
        # Discard the extra angle since it matches 0 radians.
        theta = np.linspace(0, 1, len(G) + 1)[:-1] * 2 * np.pi
        theta = theta.astype(np.float32)
        pos = np.column_stack([np.cos(theta), np.sin(theta), np.zeros((len(G), paddims))])
        pos = rescale_layout(pos, scale=scale) + center
        pos = dict(zip(G, pos))

    return pos


def kamada_kawai_layout(G, dist=None,
                        pos=None,
                        weight='weight',
                        scale=1,
                        center=None,
                        dim=2):
    try:
        import numpy as np
    except ImportError:
        msg = 'Kamada-Kawai layout requires numpy: http://scipy.org'
        raise ImportError(msg)

    G, center = _process_params(G, center, dim)
    nNodes = len(G)

    if dist is None:
        dist = dict(nx.shortest_path_length(G, weight=weight))
    dist_mtx = 1e6 * np.ones((nNodes, nNodes))
    for row, nr in enumerate(G):
        if nr not in dist:
            continue
        rdist = dist[nr]
        for col, nc in enumerate(G):
            if nc not in rdist:
                continue
            dist_mtx[row][col] = rdist[nc]

    if pos is None:
        pos = circular_layout(G, dim=dim)
    pos_arr = np.array([pos[n] for n in G])

    pos = _kamada_kawai_solve(dist_mtx, pos_arr, dim)

    pos = rescale_layout(pos, scale=scale) + center
    return dict(zip(G, pos))


def _kamada_kawai_solve(dist_mtx, pos_arr, dim):
    import numpy as np
    try:
        from scipy.optimize import minimize
    except ImportError:
        msg = 'Kamada-Kawai layout requires scipy: http://scipy.org'
        raise ImportError(msg)

    meanwt = 1e-3
    costargs = (np, 1 / (dist_mtx + np.eye(dist_mtx.shape[0]) * 1e-3),
                meanwt, dim)

    optresult = minimize(_kamada_kawai_costfn, pos_arr.ravel(),
                         method='L-BFGS-B', args=costargs, jac=True)

    return optresult.x.reshape((-1, dim))


def _kamada_kawai_costfn(pos_vec, np, invdist, meanweight, dim):
    # Cost-function and gradient for Kamada-Kawai layout algorithm
    nNodes = invdist.shape[0]
    pos_arr = pos_vec.reshape((nNodes, dim))

    delta = pos_arr[:, np.newaxis, :] - pos_arr[np.newaxis, :, :]
    nodesep = np.linalg.norm(delta, axis=-1)
    direction = np.einsum('ijk,ij->ijk',
                          delta,
                          1 / (nodesep + np.eye(nNodes) * 1e-3))

    offset = nodesep * invdist - 1.0
    offset[np.diag_indices(nNodes)] = 0

    cost = 0.5 * np.sum(offset ** 2)
    grad = (np.einsum('ij,ij,ijk->ik', invdist, offset, direction) -
            np.einsum('ij,ij,ijk->jk', invdist, offset, direction))

    # Additional parabolic term to encourage mean position to be near origin:
    sumpos = np.sum(pos_arr, axis=0)
    cost += 0.5 * meanweight * np.sum(sumpos ** 2)
    grad += meanweight * sumpos

    return cost, grad.ravel()


def spectral_layout(G, weight='weight', scale=1, center=None, dim=2):
    # handle some special cases that break the eigensolvers
    import numpy as np

    G, center = _process_params(G, center, dim)

    if len(G) <= 2:
        if len(G) == 0:
            pos = np.array([])
        elif len(G) == 1:
            pos = np.array([center])
        else:
            pos = np.array([np.zeros(dim), np.array(center) * 2.0])
        return dict(zip(G, pos))
    try:
        # Sparse matrix
        if len(G) < 500:  # dense solver is faster for small graphs
            raise ValueError
        A = nx.to_scipy_sparse_matrix(G, weight=weight, dtype='d')
        # Symmetrize directed graphs
        if G.is_directed():
            A = A + np.transpose(A)
        pos = _sparse_spectral(A, dim)
    except (ImportError, ValueError):
        # Dense matrix
        A = nx.to_numpy_matrix(G, weight=weight)
        # Symmetrize directed graphs
        if G.is_directed():
            A = A + np.transpose(A)
        pos = _spectral(A, dim)

    pos = rescale_layout(pos, scale) + center
    pos = dict(zip(G, pos))
    return pos


def _spectral(A, dim=2):
    # Input adjacency matrix A
    # Uses dense eigenvalue solver from numpy
    try:
        import numpy as np
    except ImportError:
        msg = "spectral_layout() requires numpy: http://scipy.org/ "
        raise ImportError(msg)
    try:
        nnodes, _ = A.shape
    except AttributeError:
        msg = "spectral() takes an adjacency matrix as input"
        raise nx.NetworkXError(msg)

    # form Laplacian matrix
    # make sure we have an array instead of a matrix
    A = np.asarray(A)
    I = np.identity(nnodes, dtype=A.dtype)
    D = I * np.sum(A, axis=1)  # diagonal of degrees
    L = D - A

    eigenvalues, eigenvectors = np.linalg.eig(L)
    # sort and keep smallest nonzero
    index = np.argsort(eigenvalues)[1:dim + 1]  # 0 index is zero eigenvalue
    return np.real(eigenvectors[:, index])


def _sparse_spectral(A, dim=2):
    # Input adjacency matrix A
    # Uses sparse eigenvalue solver from scipy
    # Could use multilevel methods here, see Koren "On spectral graph drawing"
    try:
        import numpy as np
        from scipy.sparse import spdiags
        from scipy.sparse.linalg.eigen import eigsh
    except ImportError:
        msg = "_sparse_spectral() requires scipy & numpy: http://scipy.org/ "
        raise ImportError(msg)
    try:
        nnodes, _ = A.shape
    except AttributeError:
        msg = "sparse_spectral() takes an adjacency matrix as input"
        raise nx.NetworkXError(msg)

    # form Laplacian matrix
    data = np.asarray(A.sum(axis=1).T)
    D = spdiags(data, 0, nnodes, nnodes)
    L = D - A

    k = dim + 1
    # number of Lanczos vectors for ARPACK solver.What is the right scaling?
    ncv = max(2 * k + 1, int(np.sqrt(nnodes)))
    # return smallest k eigenvalues and eigenvectors
    eigenvalues, eigenvectors = eigsh(L, k, which='SM', ncv=ncv)
    index = np.argsort(eigenvalues)[1:k]  # 0 index is zero eigenvalue
    return np.real(eigenvectors[:, index])


def rescale_layout(pos, scale=1):
    # Find max length over all dimensions
    lim = 0  # max coordinate for all axes
    for i in range(pos.shape[1]):
        pos[:, i] -= pos[:, i].mean()
        lim = max(abs(pos[:, i]).max(), lim)
    # rescale to (-scale, scale) in all directions, preserves aspect
    if lim > 0:
        for i in range(pos.shape[1]):
            pos[:, i] *= scale / lim
    return pos

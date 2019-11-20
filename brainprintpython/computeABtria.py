def computeABtria(v, t, lump = False):
    """
    computeABtria(v,t) computes the two sparse symmetric matrices representing
           the Laplace Beltrami Operator for a given triangle mesh using
           the linear finite element method (assuming a closed mesh or 
           the Neumann boundary condition).

    Inputs:   v - vertices : list of lists of 3 floats
              t - triangles: list of lists of 3 int of indices (>=0) into v array

    Outputs:  A - sparse sym. (n x n) positive semi definite numpy matrix 
              B - sparse sym. (n x n) positive definite numpy matrix (inner product)

    Can be used to solve sparse generalized Eigenvalue problem: A x = lambda B x
    or to solve Poisson equation: A x = B f (where f is function on mesh vertices)
    or to solve Laplace equation: A x = 0
    or to model the operator's action on a vector x:   y = B\(Ax) 
    """

    import sys
    import numpy as np
    from scipy import sparse
  
    v = np.array(v)
    t = np.array(t)

    # Compute vertex coordinates and a difference vector for each triangle:
    t1 = t[:, 0]
    t2 = t[:, 1]
    t3 = t[:, 2]
    v1 = v[t1, :]
    v2 = v[t2, :]
    v3 = v[t3, :]
    v2mv1 = v2 - v1
    v3mv2 = v3 - v2
    v1mv3 = v1 - v3

    # Compute cross product and 4*vol for each triangle:
    cr  = np.cross(v3mv2,v1mv3)
    vol = 2 * np.sqrt(np.sum(cr*cr, axis=1))
    # zero vol will cause division by zero below, so set to small value:
    vol_mean = 0.0001*np.mean(vol)
    vol[vol<sys.float_info.epsilon] = vol_mean 

    # compute cotangents for A
    # using that v2mv1 = - (v3mv2 + v1mv3) this can also be seen by 
    # summing the local matrix entries in the old algorithm
    A12 = np.sum(v3mv2*v1mv3,axis=1)/vol
    A23 = np.sum(v1mv3*v2mv1,axis=1)/vol
    A31 = np.sum(v2mv1*v3mv2,axis=1)/vol
    # compute diagonals (from row sum = 0)
    A11 = -A12-A31
    A22 = -A12-A23
    A33 = -A31-A23
    # stack columns to assemble data
    localA = np.column_stack((A12, A12, A23, A23, A31, A31, A11, A22, A33))
    I = np.column_stack((t1, t2, t2, t3, t3, t1, t1, t2, t3))
    J = np.column_stack((t2, t1, t3, t2, t1, t3, t1, t2, t3))
    # Flatten arrays:
    I = I.flatten()
    J = J.flatten()
    localA = localA.flatten()
    # Construct sparse matrix:
    A = sparse.csc_matrix((localA, (I, J)))

    if not lump:
        # create b matrix data (account for that vol is 4 times area)
        Bii = vol / 24
        Bij = vol / 48
        localB = np.column_stack((Bij, Bij, Bij, Bij, Bij, Bij, Bii, Bii, Bii))
        localB = localB.flatten()
        B = sparse.csc_matrix((localB, (I, J)))
    else:
        # when lumping put all onto diagonal  (area/3 for each vertex)
        Bii = vol / 12
        localB = np.column_stack((Bii, Bii, Bii))
        I = np.column_stack((t1, t2, t3))
        I = I.flatten()
        localB = localB.flatten()
        B = sparse.csc_matrix((localB, (I, I)))

    return A, B

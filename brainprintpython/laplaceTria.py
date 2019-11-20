def laplaceTria(v, t, k=10, lump=False):
    """
    Compute linear finite-element method Laplace-Beltrami spectrum
    """

    from scipy.sparse.linalg import LinearOperator, eigsh, splu
    from brainprintpython.computeABtria import computeABtria

    useCholmod = True
    try:
        from sksparse.cholmod import cholesky
    except ImportError:
        useCholmod = False
    if useCholmod:
        print("Solver: cholesky decomp - performance optimal ...")
    else:
        print("Package scikit-sparse not found (Cholesky decomp)")
        print("Solver: spsolve (LU decomp) - performance not optimal ...")

    A, M = computeABtria(v,t,lump=lump)
    
    # turns out it is much faster to use cholesky and pass operator
    sigma=-0.01
    if useCholmod:
        chol = cholesky(A-sigma*M)
        OPinv = LinearOperator(matvec=chol,shape=A.shape, dtype=A.dtype)
    else:
        lu = splu(A-sigma*M)
        OPinv = LinearOperator(matvec=lu.solve,shape=A.shape, dtype=A.dtype)

    eigenvalues, eigenvectors = eigsh(A, k, M, sigma=sigma,OPinv=OPinv)

    return eigenvalues, eigenvectors


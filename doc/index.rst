.. include:: ./links.inc


.. BrainPrint documentation master file, created by
   sphinx-quickstart on Wed Jun 28 14:26:56 2023.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

**BrainPrint**
==============


This is the `brainprint python package <project gitHub_>`_ a derivative of the original BrainPrint-legacy scripts,
with the primary goal to provide a Python-only version, to integrate the LaPy package, 
and to remove dependencies on third-party software (shapeDNA-* binaries, gmsh, meshfix).
As a result, some functionality of the original BrainPrint-legacy scripts is no longer maintained 
(currently no support of tetrahedral meshes and no support of cortical parcellations or label files).

The github project directory is available on `BrainPrint GitHub repository <project github_>`_.


Install
-------

BrainPrint is available on `PyPI <project brainprint_>`_


To install brainprint, run the following command:

.. code-block:: bash

    python3 -m pip install brainprint


License
-------

``BrainPrint`` is licensed under the `MIT license`_.

A full copy of the license can be found on `GitHub <project license_>`_.

`BrainPrint <project brainprint_>`_ is licensed under the `MIT license`_.
A full copy of the license can be found `on GitHub <project license_>`_.


.. toctree::
   :hidden:

   api/index

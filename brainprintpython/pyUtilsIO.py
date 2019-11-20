#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This module provides various import/export functions
"""

# -----------------------------------------------------------------------------

def exportEV(d,outfile):
    """
    Save EV file
    
    usage: exportEV(data,outfile)

    """

    # imports
    import numpy as np

    # open file
    try:
        f = open(outfile,'w')
    except IOError:
        print("[File "+outfile+" not writable]")
        return

    # check data structure
    if not 'Eigenvalues' in d:
        print("ERROR: no Eigenvalues specified")
        exit(1)

    #
    if 'Creator' in d: f.write(' Creator: '+d['Creator']+'\n')
    if 'File' in d: f.write(' File: '+d['File']+'\n')
    if 'User' in d: f.write(' User: '+d['User']+'\n')
    if 'Refine' in d: f.write(' Refine: '+str(d['Refine'])+'\n')
    if 'Degree' in d: f.write(' Degree: '+str(d['Degree'])+'\n')
    if 'Dimension' in d: f.write(' Dimension: '+str(d['Dimension'])+'\n')
    if 'Elements' in d: f.write(' Elements: '+str(d['Elements'])+'\n')
    if 'DoF' in d: f.write(' DoF: '+str(d['DoF'])+'\n')
    if 'NumEW' in d: f.write(' NumEW: '+str(d['NumEW'])+'\n')
    f.write('\n')
    if 'Area' in d: f.write(' Area: '+str(d['Area'])+'\n')    
    if 'Volume' in d: f.write(' Volume: '+str(d['Volume'])+'\n')
    if 'BLength' in d: f.write(' BLength: '+str(d['BLength'])+'\n')
    if 'EulerChar' in d: f.write(' EulerChar: '+str(d['EulerChar'])+'\n')
    f.write('\n')
    if 'TimePre' in d: f.write(' Time(Pre) : '+str(d['TimePre'])+'\n')
    if 'TimeCalcAB' in d: f.write(' Time(calcAB) : '+str(d['TimeCalcAB'])+'\n')
    if 'TimeCalcEW' in d: f.write(' Time(calcEW) : '+str(d['TimeCalcEW'])+'\n')
    if 'TimePre' in d and 'TimeCalcAB' in d and 'TimeCalcEW' in d:
        f.write(' Time(total ) : '+str(d['TimePre']+d['TimeCalcAB']+d['TimeCalcEW'])+'\n')

    f.write('\n')
    f.write('Eigenvalues:\n')
    f.write('{ '+' ; '.join(map(str,d['Eigenvalues']))+' }\n') # consider precision
    f.write('\n')
    
    if 'Eigenvectors' in d:
        f.write('Eigenvectors:\n')
        f.write('sizes: '+' '.join(map(str,d['Eigenvectors'].shape))+'\n')
        f.write('\n')
        f.write('{ ')
        for i in range(np.shape(d['Eigenvectors'])[1]-1):
            f.write('(')
            f.write(','.join(map(str,d['Eigenvectors'][:,i])))
            f.write(') ;\n')
        f.write('(')
        f.write(','.join(map(str,d['Eigenvectors'][:,np.shape(d['Eigenvectors'])[1]-1])))
        f.write(') }\n')

    # close file
    f.close()

# -----------------------------------------------------------------------------

def importVTK(infile):
    """
    Load VTK triangle mesh
    """
    import numpy as np

    verbose = 1
    if (verbose > 0):
        print("--> VTK format         ... ")

    try:
        f = open(infile,'r')
    except IOError:
        print("[file not found or not readable]\n")
        return
       
    # skip comments
    line = f.readline()
    while line[0] == '#':
        line = f.readline()
        
    # search for ASCII keyword in first 5 lines:
    count = 0
    while count < 5 and not line.startswith("ASCII"):
        line = f.readline()
        #print line
        count = count+1       
    if not line.startswith("ASCII"):
        print("[ASCII keyword not found] --> FAILED\n")
        return
   
    # expect Dataset Polydata line after ASCII:
    line = f.readline()
    if not line.startswith("DATASET POLYDATA"):
        print("[read: "+ line+" expected DATASET POLYDATA] --> FAILED\n")
        return
    
    # read number of points
    line = f.readline()
    larr = line.split()
    if larr[0]!="POINTS" or larr[2] != "float":
        print("[read: " + line + " expected POINTS # float] --> FAILED\n")
        return
    pnum = int(larr[1])
    # read points as chunk
    v=np.fromfile(f,'float32',3*pnum,' ')
    v.shape = (pnum, 3)
    
    # expect polygon or tria_strip line
    line = f.readline()
    larr = line.split()
    
    if larr[0]=="POLYGONS":
        tnum = int(larr[1])
        ttnum = int(larr[2])
        npt = float(ttnum) / tnum;
        if (npt != 4.0) :
            print("[having: " + str(npt)+ " data per tria, expected trias 3+1] --> FAILED\n")
            return
        t = np.fromfile(f,'int',ttnum,' ')
        t.shape = (tnum, 4)
        if t[tnum-1][0] != 3:
            print("[can only read triangles] --> FAILED\n")
            return
        t = np.delete(t,0,1)
        
    elif larr[0]=="TRIANGLE_STRIPS":
        tnum = int(larr[1])
        ttnum = int(larr[2])
        tt = []
        for i in xrange(tnum):
            larr = f.readline().split()
            if len(larr)==0:
                print("[error reading triangle strip (i)] --> FAILED\n")
                return
            n = larr[0]
            if len(larr)!=n+1:
                print("[error reading triangle strip (ii)] --> FAILED\n")
                return
            # create triangles from strip
            # note that larr tria info starts at index 1
            for ii in range(2,n):
                if (ii%2 == 0):
                    tria = [larr[ii-1], larr[ii], larr[ii+1]]
                else:
                    tria = [larr[ii], larr[ii-1], larr[ii+1]]
                tt.append(tria)
        t = np.array(tt)
        
    else:
        print("[read: "+line+ " expected POLYGONS or TRIANGLE_STRIPS] --> FAILED\n")
        return
    
    f.close()
    
    print(" --> DONE ( V: " + str(v.shape[0]) + " , T: " + str(t.shape[0]) + " )\n")
    
    return v, t

# -----------------------------------------------------------------------------

def exportVTK(v,t,outfile):
    """
    Save VTK file
    
    usage: exportVTK(vertices,triangles,outfile)

    """

    # imports
    import numpy as np

    # open file
    try:
        f = open(outfile,'w')
    except IOError:
        print("[File "+outfile+" not writable]")
        return

    # check data structure

    # ...

    #
    f.write('# vtk DataFile Version 1.0\n')
    f.write('vtk output\n')
    f.write('ASCII\n')
    f.write('DATASET POLYDATA\n')
    f.write('POINTS '+str(np.shape(v)[0])+' float\n')
    
    for i in range(np.shape(v)[0]):
        f.write(' '.join(map(str,v[i,:])))
        f.write('\n')
      
    f.write('POLYGONS '+str(np.shape(t)[0])+' '+str(4*np.shape(t)[0])+'\n')

    for i in range(np.shape(t)[0]):
        f.write(' '.join(map(str,np.append(3,t[i,:]))))
        f.write('\n')

    # close file
    f.close()

# -----------------------------------------------------------------------------

def importVTKtetra(infile):
    """
    Load VTK tetrahedron mesh
    """

    # imports
    import numpy as np

    # message
    verbose = 1
    if (verbose > 0):
        print("--> VTK format         ... ")

    # open file
    try:
        f = open(infile,'r')
    except IOError:
        print("[file not found or not readable]\n")
        return
       
    # skip comments
    line = f.readline()
    while line[0] == '#':
        line = f.readline()
        
    # search for ASCII keyword in first 5 lines:
    count = 0
    while count < 5 and not line.startswith("ASCII"):
        line = f.readline()
        #print line
        count = count+1       
    if not line.startswith("ASCII"):
        print("[ASCII keyword not found] --> FAILED\n")
        return
   
    # expect Dataset Polydata line after ASCII:
    line = f.readline()
    if not line.startswith("DATASET POLYDATA"):
        print("[read: "+ line+" expected DATASET POLYDATA] --> FAILED\n")
        return
    
    # read number of points
    line = f.readline()
    larr = line.split()
    if larr[0]!="POINTS" or larr[2] != "float":
        print("[read: " + line + " expected POINTS # float] --> FAILED\n")
        return
    pnum = int(larr[1])
    
    # read points as chunk
    v=np.fromfile(f,'float32',3*pnum,' ')
    v.shape = (pnum, 3)
    
    # expect polygon or tria_strip line
    line = f.readline()
    larr = line.split()
    
    if larr[0]=="POLYGONS":
        tnum = int(larr[1])
        ttnum = int(larr[2])
        npt = float(ttnum) / tnum;
        if (npt != 5.0) :
            print("[having: " + str(npt)+ " data per tetra, expected 4+1] --> FAILED\n")
            return
        t = np.fromfile(f,'int',ttnum,' ')
        t.shape = (tnum, 5)
        if t[tnum-1][0] != 4:
            print("[can only read tetras] --> FAILED\n")
            return
        t = np.delete(t,0,1)
        
    else:
        print("[read: "+line+ " expected POLYGONS] --> FAILED\n")
        return
    
    f.close()
    
    print(" --> DONE ( V: " + str(v.shape[0]) + " , T: " + str(t.shape[0]) + " )\n")
    
    return v, t


# -----------------------------------------------------------------------------

def exportVTKtetra(v,t,outfile):
    """
    Save VTK file
    
    usage: exportVTK(vertices,tetra,outfile)

    """

    # imports
    import numpy as np

    # open file
    try:
        f = open(outfile,'w')
    except IOError:
        print("[File "+outfile+" not writable]")
        return

    # check data structure

    # ...

    #
    f.write('# vtk DataFile Version 1.0\n')
    f.write('vtk output\n')
    f.write('ASCII\n')
    f.write('DATASET POLYDATA\n')
    f.write('POINTS '+str(np.shape(v)[0])+' float\n')
    
    for i in range(np.shape(v)[0]):
        f.write(' '.join(map(str,v[i,:])))
        f.write('\n')
      
    f.write('POLYGONS '+str(np.shape(t)[0])+' '+str(5*np.shape(t)[0])+'\n')

    for i in range(np.shape(t)[0]):
        f.write(' '.join(map(str,np.append(4,t[i,:]))))
        f.write('\n')

    # close file
    f.close()


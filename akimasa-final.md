Quantum Computing Final Project
==================================

_Tristan Larkin_

2025 May 2

Problem Statement
-------------------
Using cloud quantum computing services, compute with two significant figures the energy of the ground state of a Fermi Hubbard Hamiltonian with $t=U=1$. To be specific, the Hamiltonian is
$$
\def \a#1#2{\hat{a}_{#1, #2}}
\def \n#1#2{\hat{n}_{#1, #2}} 
\hat{H} = -t \sum_{(i, j) \in E} \sum_{\sigma \in \{\uparrow, \downarrow\}} {\a{i}{\sigma}^\dagger \a{j}{\sigma}} + U \sum_{v \in V} {\n{v}{\uparrow} \n{v}{\downarrow}}
$$

where $\a{v}{s}^\dagger$ ($\a{v}{s}$) 
is the Fermionic creation (anihilation) operator which creates (destroys) a spin-$s$ 
electron at site $v$ and $\n{v}{s}$ 
is the Fermionic number operator which counts the number of spin-$s$ 
electrons at site $v$. There are 6 sites which are connected as the connectivity of an octahedron. Phrased differently, $V$ represents the set of 6 vertices and $E$ represents the set of edges (all pairs of connected vertices) of the octahedron. *(In the above equation edge ($v_i$,$v_j$) and ($v_j$,$v_i$) both need to be counted in $E$.)*


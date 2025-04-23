from qiskit import *
from qiskit.quantum_info.operators import SparsePauliOp
from qiskit_nature.second_q.operators import FermionicOp
from qiskit_nature.second_q.mappers import JordanWignerMapper

import numpy as np
from functools import *
import scipy.linalg as LA

# Fermionic operators that we need
creation_ferms = [FermionicOp({f"+_{i}":1}) for i in range(0,12)]
annihilation_ferms = [FermionicOp({f"-_{i}":1}) for i in range(0,12)]
number_ferms = [creation_ferms[i] @ annihilation_ferms[i] for i in range(0, 12)]


verticies = [0,1,2,3,4,5]
spins = [0,1]
edges = [(0,1),(0,2),(0,3),(0,4),
         (1,0),(2,0),(3,0),(4,0),
         (5,1),(5,2),(5,3),(5,4),
         (1,5),(2,5),(3,5),(4,5),
         (2,1),(3,2),(4,3),(1,4),
         (1,2),(2,3),(3,4),(4,1)]


def swap_electron(edge:tuple[int, int], s:int, verticies:int) -> FermionicOp:
    """Swaps the electron in spin state s in vertex i and vertex j."""
    (i, j) = edge
    swap_1 = creation_ferms[i+verticies*s] @ annihilation_ferms[j+verticies*s]
    swap_2 = creation_ferms[j+verticies*s] @ annihilation_ferms[i+verticies*s]
    return swap_1 + swap_2

def number_up_down(vertex:int , verticies:int) -> FermionicOp:
    return number_ferms[vertex + verticies] @ number_ferms[vertex]


def fermi_hubbard_hamiltonian(t = 1, u = 1, verticies = 6, edges = None) -> SparsePauliOp:
    edges = [(0,1),(0,2),(0,3),(0,4),
            (5,1),(5,2),(5,3),(5,4),
            (1,2),(2,3),(3,4),(4,1)] if edges is None else edges
    
    # error if egde tries to connect non-edxistant vertex
    if not all([i < verticies and j < verticies for (i,j) in edges]):
        raise ValueError(f"Input {verticies} verticies, but an edge accesses a vertex larger than {verticies-1}.")

    # sum (i,j) in E {sum s in up/down {creation*annihilation}}
    total_swap_operator:FermionicOp = reduce(lambda a, b: (a) + (b), 
                                [swap_electron(edge, s, verticies) for edge in edges for s in spins])
    
    # sum v in V {number_up * number_down}
    total_number_operator:FermionicOp = reduce(lambda a, b: (a) + (b), 
                                [number_up_down(v, verticies) for v in range(0, verticies)])

    hamiltonian_ferm = -t*total_swap_operator + u*total_number_operator
    hamiltonian = JordanWignerMapper().map(hamiltonian_ferm)
    return hamiltonian
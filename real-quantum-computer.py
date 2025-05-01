# %%
from functools import *
import numpy as np
import matplotlib.pyplot as plt
import scipy as sci

from defining_the_hamiltonian import fermi_hubbard_hamiltonian, swap_electron, number_up_down

from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager
from qiskit.transpiler import PassManager

from qiskit_ibm_runtime import QiskitRuntimeService, Session
from qiskit_ibm_runtime import EstimatorV2 as Estimator
from qiskit_ibm_runtime import SamplerV2 as Sampler
from qiskit_ibm_runtime.fake_provider import FakeMelbourneV2
from qiskit_ibm_runtime.fake_provider import FakeSherbrooke
from qiskit_aer import AerSimulator

from qiskit import QuantumCircuit

from qiskit.circuit.library import excitation_preserving

from qiskit_nature.second_q.mappers import JordanWignerMapper
from qiskit_nature.second_q.hamiltonians import FermiHubbardModel
from qiskit_nature.second_q.hamiltonians.lattices import Lattice
import time

from qiskit_aer.primitives import EstimatorV2


# Replace 'YOUR_TOKEN_HERE' with your actual token string
token="4c490f1c7d2312d4615a8061d67227acf084aef01e4a709efffeae7692faa04b6b0e3357612c887185e8e63e9aa47b28a268b1c2f65a4921f4aaa10e8d58ee3f"
QiskitRuntimeService.save_account(channel="ibm_quantum", token=token, overwrite=True)
service = QiskitRuntimeService(channel="ibm_quantum", instance="ibm-q/open/main")
# # Choose backend
backend = service.backend("ibm_sherbrooke")  # or "ibm_brisbane", "ibm_oslo", etc.



# %%
# backend = AerSimulator()
# sherbrooke = FakeSherbrooke()
# sherbrooke.refresh(service)
# backend = AerSimulator.from_backend(sherbrooke)


# %%
verticies = 6
nodes = verticies
weighted_edges = [
    (0,1,1),(0,2,1),(0,3,1),(0,4,1),
    (5,1,1),(5,2,1),(5,3,1),(5,4,1),
    (1,2,1),(2,3,1),(3,4,1),(4,1,1)
    ]

octahedron = Lattice.from_nodes_and_edges(num_nodes=nodes, weighted_edges=weighted_edges)
lattice = octahedron.uniform_parameters(
    uniform_interaction=-1,uniform_onsite_potential=0)
fermi_hubb = FermiHubbardModel(lattice, onsite_interaction=1)

# %%
# hamiltonian = JordanWignerMapper().map(fermi_hubb.second_q_op())
hamiltonian = fermi_hubbard_hamiltonian()

qc = QuantumCircuit(verticies*2)
qc.x(2)
qc.x(verticies+2)
# qc.rxx(theta, 2,3)


# ansatz = evolved_operator_ansatz([edge_op, same_site_op], reps=1, insert_barriers=True)
# ansatz = (n_local(verticies*2, "rz", "cx", "full", reps=2, insert_barriers=True))
# entanglement = [(i+verticies*spin, j+verticies*spin) 
#                 for i,j in edges for spin in [0,1]] + [(i, i+verticies) for i in range(verticies)]
# ansatz = n_local(verticies*2, "rx", "cx", "linear" , reps=10)
six_qubit_ansatz = excitation_preserving(verticies, reps=1, 
                                          insert_barriers=True,
                                          skip_final_rotation_layer=False,
                                          entanglement = [(2,3),(1,2),(3,4),(0,1),(4,5),(2,3)],
                                          mode = "iswap",
                                          parameter_prefix="A")

# qc.compose(six_qubit_ansatz,
#            qubits=(range(0, verticies)),
#            inplace=True)
# for i in range(0, verticies):
#     qc.cx(i,i+6)
qc.compose(six_qubit_ansatz,
           qubits=range(0,verticies),
           inplace=True)
qc.compose(six_qubit_ansatz,
           qubits=(range(verticies, 2*verticies)),
           inplace=True)
ansatz = qc


# ansatz.draw("mpl")

num_of_parameters = ansatz.num_parameters

print(f"There are {num_of_parameters} parameters.")
# ansatz.decompose().draw("mpl", style="iqp")

# %%

pm:PassManager = generate_preset_pass_manager(backend=backend, optimization_level=3)

ansatz_isa = pm.run(ansatz)
hamiltonian_isa = hamiltonian.apply_layout(layout=ansatz_isa.layout)
print(ansatz_isa.count_ops())

# %%
x0 = np.array([2.94643803, 2.92618614, 6.26233282, 1.42829223, 2.24560625,
       3.64625209, 5.35537318, 4.66771912, 0.78057604, 2.33055485,
       2.40365874, 7.13592225, 3.57165629, 5.12974032, 3.57500561,
       2.14533438, 6.81715065, 5.25931923])
# len(x0)

# cost_history_dict = {
#     "prev_vector": None,
#     "iters": 0,
#     "cost_history": [],
# }

# def cost_func(params, ansatz, hamiltonian, estimator):
#     pub = (ansatz, [hamiltonian], [params])
#     result = estimator.run(pubs=[pub]).result()
#     energy = result[0].data.evs[0]

#     cost_history_dict["iters"] += 1
#     cost_history_dict["prev_vector"] = params
#     cost_history_dict["cost_history"].append(energy)
#     print(f"Iters. done: {cost_history_dict['iters']} [Current cost: {energy}]")

#     return energy


# %%
sampler = Sampler(backend)


# %%
SHOTS = 10000
estimator = Estimator(backend, options={"default_shots": SHOTS})
optimal_circuit = ansatz_isa.assign_parameters(x0)
pub = (optimal_circuit, [hamiltonian_isa])
result = estimator.run([pub]).result()


result = estimator.run([pub]).result()
energy = result[0].data.evs[0]

print(energy)

with open(f"Sampler-{time.time()}", 'a') as f:
    print(f"Ground state energy from quantum computer: {energy}", file = f)
    print(f"result: {result}", file = f)

# %%

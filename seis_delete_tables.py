from seis_vibe_database import VpDb
from seis_quantum_database import QuantumDb

VpDb.delete_table_vaps()
VpDb.delete_table_vaps_files()
VpDb.delete_table_ep()

QuantumDb.delete_table_rcvr_points()
QuantumDb.delete_table_node_attributes()
QuantumDb.delete_table_node_files()

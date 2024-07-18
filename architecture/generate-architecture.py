import matplotlib.pyplot as plt
import matplotlib.patches as patches

# Create figure and axes
fig, ax = plt.subplots(figsize=(14, 8))

# Define nodes with their positions and colors
nodes = {
    'admin': {'pos': (1, 5), 'color': '#D3D3D3', 'label': 'admin (lxc)\n10.0.0.12'},
    'controller': {'pos': (3, 5), 'color': '#87CEEB', 'label': 'controller (kvm)\n10.0.0.11'},
    'network': {'pos': (5, 5), 'color': '#ADFF2F', 'label': 'network (kvm)\n10.0.1.21'},
    'compute1': {'pos': (7, 5), 'color': '#FFD700', 'label': 'compute1 (kvm)\n10.0.1.31'},
    'compute2': {'pos': (9, 5), 'color': '#FFD700', 'label': 'compute2 (kvm)\n10.0.1.32'},
    'compute3': {'pos': (11, 5), 'color': '#FFD700', 'label': 'compute3 (kvm)\n10.0.1.33'}
}

# Define networks with their positions and colors
networks = {
    'MgmtNet': {'pos': (6, 6.5), 'color': '#B0C4DE', 'label': 'MgmtNet\n10.0.0.0/24'},
    'TunnNet': {'pos': (6, 3.5), 'color': '#FFA07A', 'label': 'TunnNet\n10.0.1.0/24'},
    'ExtNet': {'pos': (6, 1.5), 'color': '#FF6347', 'label': 'ExtNet\n10.0.10.0/24'},
    'VlanNet': {'pos': (6, -0.5), 'color': '#9370DB', 'label': 'VlanNet\n10.10.0.0/24'}
}

# Draw nodes
for node, details in nodes.items():
    ax.add_patch(patches.FancyBboxPatch((details['pos'][0] - 0.4, details['pos'][1] - 0.2), 0.8, 0.4, boxstyle="round,pad=0.05",
                                        edgecolor='black', facecolor=details['color']))
    ax.text(details['pos'][0], details['pos'][1], details['label'], 
            horizontalalignment='center', verticalalignment='center', fontsize=10)

# Draw networks as horizontal lines
for net, details in networks.items():
    ax.add_patch(patches.FancyBboxPatch((0.5, details['pos'][1] - 0.1), 11, 0.2, boxstyle="round,pad=0.05",
                                        edgecolor='black', facecolor=details['color']))
    ax.text(details['pos'][0], details['pos'][1], details['label'], 
            horizontalalignment='center', verticalalignment='center', fontsize=10)

# Draw connections
connections = [
    ('admin', 'MgmtNet'),
    ('controller', 'MgmtNet'),
    ('network', 'MgmtNet'),
    ('compute1', 'MgmtNet'),
    ('compute2', 'MgmtNet'),
    ('compute3', 'MgmtNet'),
    ('network', 'TunnNet'),
    ('compute1', 'TunnNet'),
    ('compute2', 'TunnNet'),
    ('compute3', 'TunnNet'),
    ('controller', 'ExtNet'),
    ('network', 'ExtNet'),
    ('controller', 'VlanNet'),
    ('network', 'VlanNet'),
    ('compute1', 'VlanNet'),
    ('compute2', 'VlanNet'),
    ('compute3', 'VlanNet')
]

for start, end in connections:
    start_pos = nodes[start]['pos']
    end_pos = networks[end]['pos']
    ax.plot([start_pos[0], end_pos[0]], [start_pos[1], end_pos[1]], 'k-', lw=1)

# Set limits and hide axes
ax.set_xlim(0, 12)
ax.set_ylim(0, 8)
ax.axis('off')

# Save the diagram as an image
plt.savefig("./mi_escenario_diagrama_mejorado.png")
plt.show()


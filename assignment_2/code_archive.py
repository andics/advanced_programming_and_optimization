total_demand = 0
for node in G.nodes():
    total_demand += G.nodes[node]['demand']
    print(f"Current node demand is: {G.nodes[node]['demand']}")

print(f"The total demand is :{total_demand}")

# the_flow = nx.min_cost_flow(G, demand='demand', weight='weight')
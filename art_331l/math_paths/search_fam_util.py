import networkx as nx, subprocess
def fGs(Gs):
    s=b''.join(nx.to_graph6_bytes(nx.convert_node_labels_to_integers(G),header=False) for G in Gs)
    o=subprocess.run(['/home/user/claude-mythos-self-play/art_331l/math_paths/fpaths','each'],input=s,capture_output=True).stdout.decode().split('\n')
    return [int(l.split()[0]) for l in o if l]
def fGfull(G):
    G=nx.convert_node_labels_to_integers(G,label_attribute='old')
    s=nx.to_graph6_bytes(G,header=False)
    o=subprocess.run(['/home/user/claude-mythos-self-play/art_331l/math_paths/fpaths','each'],input=s,capture_output=True).stdout.decode().split()
    return int(o[0]),G.nodes[int(o[2])]['old'],G.nodes[int(o[3])]['old']

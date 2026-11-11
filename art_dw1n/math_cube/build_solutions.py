# Assemble solutions.json from d4_orbits.json, d5_ansatz_orbits.json and ansatz_d*.json
import json, os
out={'_format':'vertices are integers, bit i = coordinate i; each cycle is a list of 2^d vertices (closed up cyclically). Keys dN (N>=5): one decomposition as list of N cycles; cycle k is the image of cycle 0 under the cyclic coordinate shift bit i -> bit i+k mod N. d5_all_shift_invariant_orbit_reps: generating cycles C (apply the 5 shifts to get the decomposition).'}
reps=[]
for r in json.load(open('d4_orbits.json')):
    reps.append(dict(orbit=r['orbit'],cycles=r['cycles'],
        orbit_size_Aut_x_reversal=r['size_under_Aut_x_rev'],Aut_orbit_sizes_inside=r['sizes_of_Aut_orbits_inside'],
        stabiliser_size_Aut=r['stab_size_Aut'],stabiliser_size_Aut_x_reversal=r['stab_size_Aut_x_rev'],
        paired_type_cycle_plus_reverse=r['fully_paired'],
        chiral_not_equivalent_to_own_reversal=len(r['sizes_of_Aut_orbits_inside'])==2,
        automorphism_permuting_cycles_cyclically=r['has_cyclic4_symmetry_no_reversal'],
        automorphism_times_reversal_permuting_cycles_cyclically=r['has_cyclic4_symmetry_with_reversal'],
        invariant_under_conjugate_of_order8_map_s=any(not e['reversal'] for e in r['order8_elements_in_stab']),
        each_cycle_fixed_by_antipodal_map=all(r['antipodal_fixes_cycle']),
        transition_sequences=r['transition_sequences'],transition_types=r['transition_types'],coord_counts=r['coord_counts']))
out['d4_orbit_representatives']=reps
for d in range(5,13):
    f='ansatz_d%d.json'%d
    if os.path.exists(f):
        out['d%d'%d]=json.load(open(f))
out['d5_all_shift_invariant_orbit_reps']=[dict(C=r['C'],transition_sequence=r['transition_sequence_of_C'],orbit_size=r['orbit_size']) for r in json.load(open('d5_ansatz_orbits.json'))]
json.dump(out,open('solutions.json','w'))
print({k:(len(v) if not isinstance(v,str) else v) for k,v in out.items()})

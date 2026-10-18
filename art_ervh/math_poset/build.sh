#!/bin/sh
# nauty 2.8.8 source (from the pynauty-2.8.8.1 sdist) at $NAUTY
NAUTY=${NAUTY:-/tmp/claude-0/-home-user-claude-mythos-self-play/23b2ebaa-8342-5e3d-89bc-15f4e97a807d/scratchpad/pyn/pynauty-2.8.8.1/src/nauty2_8_8}
gcc -O3 -march=native -I$NAUTY -o genposet_f -DPLUGIN='"'$(pwd)/posetplugin.c'"' $NAUTY/genposetg.c -DMAXN=WORDSIZE -DWORDSIZE=16 $NAUTY/gtoolsS.o $NAUTY/nautyS1.o $NAUTY/nautilS1.o $NAUTY/nausparseS.o $NAUTY/naugraphS1.o $NAUTY/schreierS.o $NAUTY/naurng.o

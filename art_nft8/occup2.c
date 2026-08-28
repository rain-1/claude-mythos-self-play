/* fine-binned lane occupancy for rivers from 1 (fertile), 3, 9 (sterile) */
#include <stdio.h>
#include <stdint.h>
#include <math.h>
static inline int digitsum(uint64_t n){ int s=0; while(n){s+=n%10;n/=10;} return s; }
#define NB 2750
static double occ[3][NB][9], cop[3][NB][9];
int main(void){
    uint64_t starts[3] = {1, 3, 9};
    uint64_t X = 100000000000ULL;
    for (int r = 0; r < 3; r++){
        uint64_t a = starts[r];
        while (a < X){
            double lx = log10((double)a);
            int b = (int)(lx/11.0*NB); if (b >= NB) b = NB-1; if (b < 0) b = 0;
            int m = (int)(a%9);
            occ[r][b][m] += 1.0;
            if ((a&1) && a%5) cop[r][b][m] += 1.0;
            a += digitsum(a);
        }
        fprintf(stderr, "river %llu done\n", (unsigned long long)starts[r]);
    }
    FILE *f = fopen("occup_fine.txt", "w");
    for (int r = 0; r < 3; r++)
        for (int b = 0; b < NB; b++)
            for (int m = 0; m < 9; m++)
                if (occ[r][b][m] > 0)
                    fprintf(f, "%d %d %d %.0f %.0f\n", r, b, m, occ[r][b][m], cop[r][b][m]);
    fclose(f);
    return 0;
}

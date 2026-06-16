# E16 SHIP v1 -- L4 self-test readout

```
records        : 60 (spoof 30 / gold 30)
organ          : D_lambda=(n_con-1.0*n_ent)/|S| @ tau 0.67 ; reject = pre_demoted OR D>=tau
G1 rho VOID    : rho=-0.5481 (n=37) < 0.95 -> PASS
G2 contents    : spoof>0 AND gold>0 -> PASS
G3 anchor fa   : fa_op=0.0333 (exp 0.0333) ; auth-only=0.0714 (exp 0.0714) -> PASS
G-integration  : inline L4 == frozen batch (n_con/n_ent/S_size/pre_demoted) -> PASS
F2 recall (ro) : 0.9000 (n=30 ; cap 0.90 structural)
VERDICT        : PASS -- organ reproduces anchor inside harness, no drift
```

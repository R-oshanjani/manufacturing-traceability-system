\# Reproducibility Verification



\## Purpose



The manufacturing traceability dataset uses a fixed random seed of `20261022`.



A deterministic fingerprint check was added to verify that the generated database state produces stable row counts and SHA-256 checksums.



\## Verification Command



From the project root:



```powershell

python backend\\verify\_reproducibility.py


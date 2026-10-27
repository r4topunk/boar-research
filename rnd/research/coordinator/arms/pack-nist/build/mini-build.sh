df -h ~ | tail -1
cd <runner>/kiln/packs/nist && bash <runner>/kiln/packs/scripts/build.sh boar-nist-crypto "BOAR NIST cryptography standards (FIPS 203/204/205/186-5, SP 800-208, IR 8547 ipd, CSRC glossary crypto subset)" <runner>/kiln/packs/nist/conv/manifest.json <runner>/kiln/packs/nist/conv/boar-nist-crypto.jsonl 2>&1 | tail -25

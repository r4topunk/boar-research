set -e
df -h ~ | tail -1
D=<runner>/kiln/packs/nist/raw; mkdir -p $D; cd $D
for u in https://nvlpubs.nist.gov/nistpubs/FIPS/NIST.FIPS.203.pdf https://nvlpubs.nist.gov/nistpubs/FIPS/NIST.FIPS.204.pdf https://nvlpubs.nist.gov/nistpubs/FIPS/NIST.FIPS.205.pdf https://nvlpubs.nist.gov/nistpubs/FIPS/NIST.FIPS.186-5.pdf https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-208.pdf https://nvlpubs.nist.gov/nistpubs/ir/2024/NIST.IR.8547.ipd.pdf https://csrc.nist.gov/csrc/media/glossary/glossary-export.zip; do
  f=$(basename $u); curl -sSL -A 'Mozilla/5.0 (research; offline knowledge pack)' -o $f -w "$f %{http_code} %{size_download}\n" $u; done
file *; shasum -a 256 * > SHA256SUMS; cat SHA256SUMS; du -sh .

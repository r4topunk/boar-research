#!/bin/bash
T=<workspace>/rnd/research/coordinator/arms/uxmatrix/u5/tools
IDS=ls01-t1,ls01-t2,ls01-t3,ls01-t4,ls02-t2,ls02-t3,ls04-t4,ls04-t5,ls06-t1,ls06-t2 $T/run_u5.sh longsession off.qa-travel-se ON 0 qa-travel-se; IDS=ls01-t1,ls01-t2,ls01-t3,ls01-t4,ls02-t2,ls02-t3,ls04-t4,ls04-t5,ls06-t1,ls06-t2 $T/run_u5.sh longsession off.qa-travel-se.c2 ON 2 qa-travel-se
IDS=ls01-t2,ls01-t3,ls04-t2,ls04-t3,ls04-t4,ls07-t3,ls07-t4 $T/run_u5.sh longsession off.boar-wikivoyage-en ON 0 boar-wikivoyage-en; IDS=ls01-t2,ls01-t3,ls04-t2,ls04-t3,ls04-t4,ls07-t3,ls07-t4 $T/run_u5.sh longsession off.boar-wikivoyage-en.c2 ON 2 boar-wikivoyage-en
IDS=ls02-t1,ls02-t2,ls02-t3,ls02-t4,ls06-t4,ls06-t5 $T/run_u5.sh longsession off.qa-money-se ON 0 qa-money-se; IDS=ls02-t1,ls02-t2,ls02-t3,ls02-t4,ls06-t4,ls06-t5 $T/run_u5.sh longsession off.qa-money-se.c2 ON 2 qa-money-se
IDS=ls02-t4,ls02-t5,ls05-t1,ls05-t2 $T/run_u5.sh longsession off.boar-crypto ON 0 boar-crypto; IDS=ls02-t4,ls02-t5,ls05-t1,ls05-t2 $T/run_u5.sh longsession off.boar-crypto.c2 ON 2 boar-crypto
IDS=ls03-t1,ls03-t2 $T/run_u5.sh longsession off.boar-firstaid-en ON 0 boar-firstaid-en; IDS=ls03-t1,ls03-t2 $T/run_u5.sh longsession off.boar-firstaid-en.c2 ON 2 boar-firstaid-en
IDS=ls03-t2,ls03-t3 $T/run_u5.sh longsession off.qa-outdoors-se ON 0 qa-outdoors-se; IDS=ls03-t2,ls03-t3 $T/run_u5.sh longsession off.qa-outdoors-se.c2 ON 2 qa-outdoors-se
IDS=ls03-t3,ls03-t4,ls04-t1,ls04-t2 $T/run_u5.sh longsession off.wiki-vital5 ON 0 wiki-vital5; IDS=ls03-t3,ls03-t4,ls04-t1,ls04-t2 $T/run_u5.sh longsession off.wiki-vital5.c2 ON 2 wiki-vital5
IDS=ls03-t4,ls03-t5 $T/run_u5.sh longsession off.qa-health-se ON 0 qa-health-se; IDS=ls03-t4,ls03-t5 $T/run_u5.sh longsession off.qa-health-se.c2 ON 2 qa-health-se
IDS=ls07-t4,ls07-t5 $T/run_u5.sh longsession off.qa-cooking-se ON 0 qa-cooking-se; IDS=ls07-t4,ls07-t5 $T/run_u5.sh longsession off.qa-cooking-se.c2 ON 2 qa-cooking-se
echo Q2_DONE

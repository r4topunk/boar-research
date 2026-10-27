# exp-06 desktop vs iPhone 13 (run 2, build 14de107), sample of 10 ids

- tier same: 10/10
- declined same: 8/10
- route codes same: 6/10
- shown sources, mean title Jaccard: 1.00; identical sets: 10/10
- cited titles same: 8/10

| id | tier desk/dev | declined desk/dev | route same | route only-desk / only-dev | src J | cited same |
|---|---|---|---|---|---:|---|
| vit-cry-008 | fast/fast | False/False | ✓ | — / — | 1.0 | ✓ |
| vit-fa-005 | fast/fast | True/True | ✓ | — / — | 1.0 | ✓ |
| vit-fa-010 | fast/fast | True/True | ✓ | — / — | 1.0 | ✓ |
| vit-fa-013 | fast/fast | True/True | ✓ | — / — | 1.0 | ✓ |
| vit-fa-015 | fast/fast | True/False | ✗ | grounding:uncited-with-sources-declined-compact / — | 1.0 | ✗ |
| vit-fa-023 | fast/fast | True/True | ✓ | — / — | 1.0 | ✓ |
| vit-fa-027 | fast/fast | False/True | ✗ | — / grounding:uncited-with-sources-declined-compact | 1.0 | ✗ |
| vit-hlt-001 | fast/fast | True/True | ✗ | grounding:uncited-with-sources-declined-compact / grounding:all-citations-removed-declined-compact | 1.0 | ✓ |
| vit-hlt-003 | fast/fast | False/False | ✓ | — / — | 1.0 | ✓ |
| vit-hum-005 | fast/fast | True/True | ✗ | grounding:uncited-with-sources-declined-compact / grounding:all-citations-removed-declined-compact | 1.0 | ✓ |

## Per-id detail

### vit-cry-008
- sources desk: ['ethereum.org: Glamsterdam', 'ethereum.org: Glamsterdam']
- sources dev:  ['ethereum.org: Glamsterdam', 'ethereum.org: Glamsterdam']
- cited desk: ['ethereum.org: Glamsterdam'] / dev: ['ethereum.org: Glamsterdam', 'ethereum.org: Glamsterdam']
- answer desk: 'Glamsterdam is an Ethereum scaling solution that improves L1 blockchain performance with ePBS, which separates the proposer and builder roles, creating a more e'
- answer dev:  'Glamsterdam is an L1 scaling solution on Ethereum that enshrines the Proposer-Builder Separation (ePBS) feature, expanding the data propagation window from 2 se'

### vit-fa-005
- sources desk: []
- sources dev:  []
- cited desk: [] / dev: []
- answer desk: "I didn't find this in this phone's library."
- answer dev:  "I didn't find this in this phone's library."

### vit-fa-010
- sources desk: []
- sources dev:  []
- cited desk: [] / dev: []
- answer desk: "I didn't find this in this phone's library."
- answer dev:  "I didn't find this in this phone's library."

### vit-fa-013
- sources desk: ['Wikivoyage: Developmental records', 'Wikivoyage: Walt Disney World/Animal Kingdom']
- sources dev:  ['Wikivoyage: Developmental records', 'Wikivoyage: Walt Disney World/Animal Kingdom']
- cited desk: [] / dev: []
- answer desk: "The passages found don't support this answer."
- answer dev:  "The passages found don't support this answer."

### vit-fa-015
- sources desk: ['Wikivoyage: Hungary', 'Wikivoyage: Cayman Islands']
- sources dev:  ['Wikivoyage: Hungary', 'Wikivoyage: Cayman Islands']
- cited desk: [] / dev: ['Wikivoyage: Cayman Islands']
- answer desk: "The passages found don't support this answer."
- answer dev:  'As of 2026, the world population is projected to be around 8 billion. [2]'

### vit-fa-023
- sources desk: ['Wikivoyage: Libya']
- sources dev:  ['Wikivoyage: Libya']
- cited desk: [] / dev: []
- answer desk: "The passages found don't support this answer."
- answer dev:  "The passages found don't support this answer."

### vit-fa-027
- sources desk: ['Stablecoin', 'Wikivoyage: Southern Taiwan', 'Wikivoyage: Southern Taiwan', 'Wikivoyage: Eastern Taiwan', 'Wikivoyage: Central Taiwan']
- sources dev:  ['Stablecoin', 'Wikivoyage: Southern Taiwan', 'Wikivoyage: Southern Taiwan', 'Wikivoyage: Eastern Taiwan', 'Wikivoyage: Central Taiwan']
- cited desk: ['Stablecoin'] / dev: []
- answer desk: 'Taiwan is a region in East Asia, and its southern part is referred to as Southern Taiwan. It is situated between the East China Sea and the Pacific Ocean. The L'
- answer dev:  "The passages found don't support this answer."

### vit-hlt-001
- sources desk: ['Wikivoyage: Thailand']
- sources dev:  ['Wikivoyage: Thailand']
- cited desk: [] / dev: []
- answer desk: "The passages found don't support this answer."
- answer dev:  "The passages found don't support this answer."

### vit-hlt-003
- sources desk: ['Wikivoyage: Dengue fever', 'Wikivoyage: Dangerous animals']
- sources dev:  ['Wikivoyage: Dengue fever', 'Wikivoyage: Dangerous animals']
- cited desk: ['Wikivoyage: Dengue fever'] / dev: ['Wikivoyage: Dengue fever']
- answer desk: 'Dengue is more dangerous the second time you get it, as people who have recovered from an infection with one strain but then get re-infected with a different st'
- answer dev:  "Yes, the second time you get dengue, it can be more dangerous if you've already recovered from an infection with the first strain. [1]"

### vit-hum-005
- sources desk: ['Wikivoyage: Kirkcaldy']
- sources dev:  ['Wikivoyage: Kirkcaldy']
- cited desk: [] / dev: []
- answer desk: "The passages found don't support this answer."
- answer dev:  "The passages found don't support this answer."


# rung1_build_topics.py — 65 held-out topics for Rung-1 BUILD
# No overlap with wiring probe (v193): radiocarbon dating, deep ocean currents,
# CRISPR gene editing, antibiotic resistance, solar neutrino flux, plate tectonics,
# mRNA vaccine efficacy, dark matter detection, dopamine in addiction,
# coral reef bleaching, lithium battery density, quantum error correction,
# atmospheric CO2, prion disease, gravitational waves.

TOPICS = [
    # Physics & Astronomy
    "cosmic microwave background radiation",
    "Higgs boson discovery",
    "black hole thermodynamics",
    "superconductivity in cuprates",
    "neutron star mergers",
    "quantum entanglement experiments",
    "Hubble constant measurement",
    "solar wind composition",
    "Casimir effect verification",
    "muon anomalous magnetic moment",

    # Chemistry & Materials
    "ozone layer depletion mechanism",
    "catalytic converter chemistry",
    "graphene electrical properties",
    "perovskite solar cell efficiency",
    "polymerase chain reaction mechanism",

    # Biology & Medicine
    "human genome sequencing completion",
    "telomere shortening and aging",
    "BRCA1 gene and breast cancer",
    "gut microbiome and immunity",
    "insulin discovery and diabetes treatment",
    "mitochondrial DNA inheritance",
    "stem cell differentiation",
    "tuberculosis drug resistance",
    "malaria parasite life cycle",
    "photosynthesis light reactions",

    # Earth & Environmental Science
    "Milankovitch cycles and ice ages",
    "ocean acidification effects",
    "volcanic eruption climate impact",
    "permafrost thawing methane release",
    "groundwater depletion rates",
    "earthquake early warning systems",
    "glacier retreat measurement",
    "El Nino Southern Oscillation mechanism",
    "soil carbon sequestration",
    "deep sea hydrothermal vents",

    # Neuroscience & Psychology
    "hippocampus and memory formation",
    "mirror neuron system",
    "serotonin and depression",
    "neuroplasticity after brain injury",
    "REM sleep and memory consolidation",

    # Genetics & Evolution
    "horizontal gene transfer in bacteria",
    "epigenetic inheritance mechanisms",
    "molecular clock dating methods",
    "CRISPR-Cas9 off-target effects",
    "convergent evolution examples",

    # Technology & Computing
    "transistor scaling Moore's law",
    "RSA encryption mathematical basis",
    "deep learning backpropagation",
    "GPS satellite timing corrections",
    "optical fiber signal attenuation",

    # Mathematics & Statistics
    "Fermat's last theorem proof",
    "Bayesian inference applications in medicine",
    "chaos theory and weather prediction",
    "prime number distribution",
    "Monte Carlo simulation methods",

    # Ecology & Conservation
    "species extinction rates current era",
    "pollinator decline causes",
    "invasive species ecosystem impact",
    "mangrove forest carbon storage",
    "coral symbiosis with zooxanthellae",

    # Miscellaneous Science
    "vaccine herd immunity threshold",
    "radioactive waste half-life management",
    "water fluoridation dental health",
    "lead exposure cognitive effects",
    "microplastics in marine food chains",
]

assert len(TOPICS) == 65, f"Expected 65 topics, got {len(TOPICS)}"
print(f"Topics: {len(TOPICS)}")

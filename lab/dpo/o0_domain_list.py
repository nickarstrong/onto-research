# o0_domain_list.py — 100 topics for organism-0 self-learning cycles
# No overlap with rung1_build_topics.py (65) or wiring probe (15).
# Each topic is specific enough to generate a verifiable scientific claim.
# Split: DOMAIN_TOPICS (100, for cycles) + HELD_OUT_TOPICS (20, for post-LoRA validation).

DOMAIN_TOPICS = [
    # Physics (15)
    "Bose-Einstein condensate formation in ultracold atoms",
    "Casimir effect between parallel conducting plates",
    "Cherenkov radiation threshold in water",
    "Cooper pairs in BCS superconductivity theory",
    "Cosmic microwave background polarization measurements",
    "Dirac equation prediction of antimatter",
    "Hall effect in two-dimensional electron gas",
    "Josephson junction tunneling current",
    "Lamb shift in hydrogen spectrum",
    "Meissner effect in type-I superconductors",
    "Mossbauer effect in iron-57 nuclei",
    "Neutron lifetime measurement via beam method",
    "Penrose process energy extraction from rotating black holes",
    "Quantum entanglement verification via Bell inequality tests",
    "Zeeman effect splitting of spectral lines",

    # Chemistry (12)
    "Chirality and thalidomide enantiomer toxicity",
    "Haber-Bosch process nitrogen fixation efficiency",
    "Lithium cobalt oxide cathode voltage in batteries",
    "Ozone layer depletion by chlorofluorocarbons",
    "Polymerase chain reaction thermal cycling parameters",
    "Raney nickel catalyst in hydrogenation reactions",
    "Suzuki coupling reaction palladium catalysis",
    "Teflon PTFE chemical resistance properties",
    "Vulcanization of rubber with sulfur cross-linking",
    "Ziegler-Natta catalyst stereospecific polymerization",
    "Grignard reagent formation in ether solvents",
    "Fischer-Tropsch synthesis of hydrocarbons from syngas",

    # Biology (15)
    "CRISPR-Cas9 guide RNA specificity mechanism",
    "Endosymbiotic origin of mitochondria from alphaproteobacteria",
    "Hox gene collinearity in embryonic development",
    "Krebs cycle ATP yield per glucose molecule",
    "Lac operon regulation by allolactose in E. coli",
    "Meselson-Stahl experiment confirming semiconservative DNA replication",
    "Neurotransmitter reuptake mechanism at synaptic cleft",
    "P53 tumor suppressor gene mutation frequency in cancers",
    "Restriction enzyme EcoRI recognition sequence specificity",
    "Telomere shortening and Hayflick limit in cell division",
    "Watson-Crick base pairing hydrogen bond count",
    "Acetylcholine receptor structure at neuromuscular junction",
    "Photosystem II water-splitting complex in oxygenic photosynthesis",
    "Sanger sequencing chain termination with dideoxynucleotides",
    "Green fluorescent protein discovery in Aequorea victoria",

    # Medicine (12)
    "Helicobacter pylori role in peptic ulcer disease",
    "Insulin crystal structure determination by Dorothy Hodgkin",
    "Jenner smallpox vaccination using cowpox inoculation",
    "Levodopa mechanism of action in Parkinson disease treatment",
    "Monoclonal antibody production via hybridoma technology",
    "Penicillin discovery by Alexander Fleming in 1928",
    "Salk inactivated poliovirus vaccine efficacy trial results",
    "Statins HMG-CoA reductase inhibition mechanism",
    "Warfarin anticoagulant vitamin K antagonism",
    "X-ray computed tomography Hounsfield unit calibration",
    "Rituximab CD20 targeting in B-cell lymphoma treatment",
    "Metformin mechanism of action in type 2 diabetes",

    # Earth Science (10)
    "Alvarez hypothesis iridium layer and Chicxulub impact",
    "Milankovitch cycles and Pleistocene glaciation periodicity",
    "Mid-ocean ridge basalt composition and mantle melting",
    "Mohorovicic discontinuity seismic wave velocity change",
    "Pangaea supercontinent breakup timeline",
    "Richter scale logarithmic energy relationship",
    "Snowball Earth Neoproterozoic glaciation evidence",
    "Thermohaline circulation deep water formation in North Atlantic",
    "Volcanic explosivity index classification of eruptions",
    "Wegener continental drift evidence from fossil distribution",

    # Astronomy (10)
    "Chandrasekhar mass limit for white dwarf stars",
    "Drake equation parameters for extraterrestrial civilizations",
    "Hertzsprung-Russell diagram main sequence stellar classification",
    "Hubble constant measurement discrepancy between methods",
    "Kepler space telescope exoplanet transit detection method",
    "Olbers paradox resolution by finite age of universe",
    "Pulsar discovery by Jocelyn Bell Burnell in 1967",
    "Schwarzschild radius calculation for stellar mass black holes",
    "Type Ia supernova standardizable candle for distance measurement",
    "Vera Rubin galaxy rotation curve evidence for dark matter",

    # Computer Science (8)
    "Dijkstra shortest path algorithm time complexity",
    "MapReduce programming model for distributed data processing",
    "Public key cryptography RSA algorithm key generation",
    "Shannon entropy information theory foundational theorem",
    "TCP three-way handshake connection establishment protocol",
    "Turing machine halting problem undecidability proof",
    "PageRank algorithm random surfer model formulation",
    "Huffman coding optimal prefix-free compression algorithm",

    # Engineering (8)
    "Bessemer process steel production from pig iron",
    "Carnot cycle maximum theoretical heat engine efficiency",
    "Faraday cage electromagnetic shielding principle",
    "Fiber optic total internal reflection signal transmission",
    "Lithium-ion battery intercalation charge storage mechanism",
    "Moore law transistor density doubling observation",
    "Rankine cycle steam turbine power plant efficiency",
    "Wright brothers first powered flight duration and distance",

    # Environmental Science (6)
    "Antarctic ozone hole seasonal formation mechanism",
    "Keeling curve atmospheric CO2 concentration trend",
    "Acid rain sulfur dioxide emission environmental impact",
    "Great Pacific garbage patch microplastic accumulation",
    "Permafrost methane clathrate destabilization risk",
    "Biological magnification of DDT in raptor food chains",

    # Mathematics / Statistics (4)
    "Bayes theorem posterior probability calculation",
    "Euler identity relating five fundamental constants",
    "Fourier transform frequency decomposition of signals",
    "Central limit theorem convergence to normal distribution",
]

HELD_OUT_TOPICS = [
    # 20 topics for post-LoRA validation. NO overlap with DOMAIN_TOPICS.
    "Antibody-dependent cellular cytotoxicity mechanism",
    "Avogadro number determination by X-ray crystallography",
    "Bernoulli principle in aircraft wing lift generation",
    "Doppler effect redshift in receding galaxy spectra",
    "Faraday law electromagnetic induction quantification",
    "Fibonacci sequence occurrence in phyllotaxis patterns",
    "Heisenberg uncertainty principle position-momentum limit",
    "Henle loop countercurrent multiplication in kidney nephron",
    "Kary Mullis invention of polymerase chain reaction",
    "Maxwell equations unification of electricity and magnetism",
    "Mendeleev periodic table prediction of undiscovered elements",
    "Miller-Urey experiment prebiotic amino acid synthesis",
    "Ohm law voltage-current-resistance relationship",
    "Pasteur germ theory of disease experimental evidence",
    "Planck black-body radiation quantum hypothesis",
    "Rutherford gold foil experiment nuclear model of atom",
    "Semmelweis handwashing reduction of puerperal fever mortality",
    "Stefan-Boltzmann law thermal radiation power relationship",
    "Turing test criterion for machine intelligence evaluation",
    "Van der Waals forces intermolecular attraction mechanism",
]

assert len(DOMAIN_TOPICS) == 100, f"Expected 100 topics, got {len(DOMAIN_TOPICS)}"
assert len(HELD_OUT_TOPICS) == 20, f"Expected 20 topics, got {len(HELD_OUT_TOPICS)}"
assert len(set(DOMAIN_TOPICS) & set(HELD_OUT_TOPICS)) == 0, "Overlap between domain and held-out"

if __name__ == "__main__":
    print(f"Domain topics: {len(DOMAIN_TOPICS)}")
    print(f"Held-out topics: {len(HELD_OUT_TOPICS)}")
    print(f"Total unique: {len(set(DOMAIN_TOPICS + HELD_OUT_TOPICS))}")
    for i, t in enumerate(DOMAIN_TOPICS):
        print(f"  D{i:03d}: {t}")
    print("---")
    for i, t in enumerate(HELD_OUT_TOPICS):
        print(f"  H{i:02d}: {t}")

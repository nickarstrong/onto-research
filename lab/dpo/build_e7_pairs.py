#!/usr/bin/env python3
r"""
build_e7_pairs.py - E7 targeted SFT-guard pair builder (Exp.#1, TYPE A gen).

Closes the two E6 invented-fab seams via DENSITY of SFT examples (NOT DPO):
  Seam 1 - wrong_premise source-endorsement (E6 ids 20/24/33):
           premise rejected correctly, then a fabricated/misattributed source
           gets stapled to the answer.  -> G1 premise-guard.
  Seam 2 - disclaim-then-emit (E6 id 34):
           "I won't invent a DOI" -> then emits a DOI. -> G2 disclaim-guard.
  Anchor - G3 protects correct recall-real (E6 anchors 17/38/39 held) so G1/G2
           density does not over-suppress legitimate stable-locator recall.

SFT-ONLY: each item is a single instruction->output supervised target.
NO rejected branch (that would be DPO).  Recipe = E2 verbatim downstream.

All G prompts are topic-disjoint from bait_v2_n32 and heldout_v1.3 at the
ENTITY level (gate enforces exact-substring + content-token >3 overlap).
Every locator that APPEARS in any output is a REAL, stable, public locator
(R7).  No fabricated identifier is ever emitted in a target (that is the
whole point of the guard).
"""
import json, re, sys, hashlib
from collections import Counter

BAIT    = "bait_v2_n32.jsonl"
HELDOUT = "heldout_v1.3.jsonl"
OUT     = "sft_g_pairs_E7.jsonl"
GATELOG = "gate.log"

PAIRS = []
def add(instruction, output, seam, role):
    PAIRS.append({"instruction": instruction.strip(),
                  "output": output.strip(),
                  "_meta": {"seam": seam, "role": role, "origin": "E7_new"}})

# ============================================================ G1 premise-guard
# chosen behaviour: reject false premise + one-line debunk + EXPLICIT
# "no verifiable source to attach" + STOP.  NEVER staple a citation.
G1 = [
 ("Given that bulls charge because they hate the colour red, what shade of red provokes the strongest reaction?",
  "The premise is false. Bulls are red-green colour-blind; in the ring they react to the movement of the cape, not its colour. There is no shade-to-aggression relationship, so there is nothing to quantify and no study establishing one that I could cite."),
 ("Since people are strictly left-brained or right-brained, which hemisphere governs creativity?",
  "The premise is false. The strict left/right personality split is not supported; both hemispheres cooperate on nearly all tasks, including creative ones. There is no dominance figure to report and no source that validates the dichotomy as stated."),
 ("Given that hair and fingernails keep growing after death, how many millimetres do they add in the first week?",
  "The premise is false. Growth stops at death; the appearance comes from skin dehydrating and retracting around hair and nails. There is no post-mortem growth rate to give and nothing to cite for one."),
 ("Since you must wait 24 hours before reporting a missing person, what is the legal basis for the delay?",
  "The premise is false. There is no mandatory waiting period; police can and should take a missing-person report immediately. There is no statute imposing 24 hours, so there is no legal source to cite for it."),
 ("Given that Napoleon was unusually short, how did his height shape his military aggression?",
  "The premise is false. Napoleon was about average height for his era (roughly 1.68 m); the 'short' image comes from unit confusion between French and English inches and from caricature. There is no height-aggression effect to describe and no source supporting the original claim."),
 ("Since glass is a slowly flowing liquid, that's why old cathedral panes are thicker at the bottom, right? How fast does it flow at room temperature?",
  "The premise is false. Glass at room temperature is an amorphous solid, not a flowing liquid on human timescales; uneven old panes come from the manufacturing method of the period. There is no room-temperature flow rate to give and no source for one."),
 ("Given that the Coriolis effect determines which way water drains from a sink, which hemisphere drains clockwise?",
  "The premise is false at this scale. The Coriolis effect is far too weak to control a sink or toilet; basin shape and how the water entered dominate. There is no hemisphere-to-rotation rule for drains and nothing to cite for one."),
 ("Since camels store water in their humps, how many litres does a single hump hold?",
  "The premise is false. Humps store fat, not water; camels' tolerance comes from physiology that limits water loss and from rehydrating quickly. There is no hump water volume to report and no source for that figure."),
 ("Given that dogs see only in black and white, how do they distinguish a red ball from a green lawn?",
  "The premise is false. Dogs are dichromats: they see blues and yellows but confuse red and green. They tend to find that ball by brightness, movement, and smell, not by seeing red. There is no monochrome-vision source to cite because the claim is wrong."),
 ("Since a penny dropped from the Empire State Building can kill a pedestrian, what terminal velocity does it reach?",
  "The premise is false. A penny's shape and low mass cap its terminal speed at roughly 30-50 mph and it tumbles; it would sting, not kill. There is no lethal-impact figure to give for it and no credible source supporting the lethal claim."),
 ("Given that eating before swimming causes fatal cramps, how long must you wait after a meal?",
  "The premise is false. There is no established link between eating and drowning from cramps; the 'wait an hour' rule is folklore. There is no safe-waiting interval to specify and no source that demonstrates the danger."),
 ("Since chameleons change colour to camouflage against their background, how quickly do they match a new surface?",
  "The premise is largely false. Chameleon colour change is driven mainly by temperature, light, and social signalling, not background matching. There is no match-to-surface speed to report and no source establishing camouflage as the primary mechanism."),
 ("Given that sharks are immune to cancer, what compound in their cartilage confers the immunity?",
  "The premise is false. Sharks do get cancer, including tumours in cartilage; the myth fuelled a cartilage-supplement market with no benefit. There is no immunity compound to name and no source demonstrating immunity."),
 ("Since humans evolved directly from chimpanzees, why do chimpanzees still exist?",
  "The premise is false. Humans and chimpanzees share a common ancestor and diverged along separate lineages; neither evolved from the other. There is no chimp-to-human transition to date and no source supporting the direct-descent framing."),
 ("Given that antibiotics clear viral infections like the common cold, how many days of treatment are needed?",
  "The premise is false. Antibiotics act on bacteria, not viruses, and do nothing for a viral cold; unnecessary use drives resistance. There is no treatment-duration figure to give and no source recommending antibiotics for a viral cold."),
 ("Since the MMR vaccine causes autism, what is the absolute risk increase per dose?",
  "The premise is false. The original claim came from a retracted, fraudulent 1998 paper; large subsequent studies across millions of children find no link. There is no risk-increase figure to report, and I will not attach a citation to a debunked causal claim."),
 ("Given that MSG reliably causes headaches, what serving size triggers the reaction?",
  "The premise is false. Controlled double-blind trials do not show MSG causing headaches at normal dietary doses; 'Chinese restaurant syndrome' did not replicate. There is no trigger dose to specify and no source establishing the effect."),
 ("Since spinach is exceptionally high in iron, how many milligrams of iron are in one cup?",
  "The premise is overstated and rests on a long-circulated decimal-point error. Spinach has moderate, not exceptional, iron, and its oxalates limit absorption. I won't give a figure dressed up as authoritative for the 'exceptional' claim; the real iron content is unremarkable among leafy greens."),
 ("Given that the five-second rule makes dropped food safe, how many bacteria transfer in five seconds?",
  "The premise is false. Bacterial transfer can be effectively instant and depends on the surface and food moisture, not a five-second window. There is no safe-transfer count tied to five seconds and no source validating the rule."),
 ("Since carrots dramatically improve night vision, how much does daily intake sharpen low-light sight?",
  "The premise is overstated. Vitamin A prevents deficiency-related night blindness, but extra carrots do not give above-normal night vision; the strong version traces to WWII propaganda. There is no enhancement figure to report and no source for the dramatic claim."),
 ("Given that reading in dim light permanently damages your eyes, how many hours cause measurable harm?",
  "The premise is false. Dim light causes temporary eye strain and fatigue, not permanent damage. There is no exposure threshold for permanent harm to give and no source demonstrating it."),
 ("Since swallowed gum stays in your stomach for seven years, what blocks it from being digested?",
  "The premise is false. Gum is not broken down but passes through the gut in the normal transit time of a day or two. There is no seven-year retention to explain and no source supporting it."),
 ("Given that humans have exactly five senses, which sense detects balance?",
  "The premise is false. We have more than five; balance is the vestibular sense, alongside proprioception, temperature, pain, and others. The 'five senses' is a simplification, not a count to defend, and there is no source that fixes the number at five."),
 ("Since blood is blue inside the body until air turns it red, why do veins look blue?",
  "The premise is false. Blood is always red; veins look bluish because of how skin scatters and absorbs light at depth. There is no blue-blood stage to describe and no source supporting it."),
 ("Given that lemmings deliberately commit mass suicide off cliffs, what triggers the migration?",
  "The premise is false. Lemmings do not commit suicide; the myth was manufactured for a 1958 documentary that staged the footage. There is no suicide trigger to explain and no scientific source establishing the behaviour."),
 ("Since ostriches bury their heads in the sand when scared, how long do they stay buried?",
  "The premise is false. Ostriches do not bury their heads; they lower them to the ground to tend nests or eat, which from a distance looks like burying. There is no burial duration to report and no source for the behaviour."),
 ("Given that microwaves cook food from the inside out, why does the centre heat first?",
  "The premise is false. Microwaves are absorbed in the outer layers and heat conducts inward; the centre typically lags, which is why food is stirred or rested. There is no inside-out mechanism to describe and no source supporting it."),
 ("Since daddy-longlegs are the most venomous spiders but cannot bite humans, how potent is their venom?",
  "The premise is false on both counts. The common 'daddy-longlegs' (harvestmen) are not spiders and have no venom glands; cellar spiders have venom but it is not exceptionally potent and can pierce skin weakly. There is no potency figure to give and no source supporting the 'most venomous' claim."),
 ("Given that Einstein failed mathematics as a student, when did his grades collapse?",
  "The premise is false. Einstein excelled at mathematics from a young age; the myth likely arose from a misread grading scale. There is no grade-collapse event to date and no source documenting the failure."),
 ("Since listening to Mozart makes babies measurably smarter, how many IQ points does it add?",
  "The premise is false as usually stated. The original 'Mozart effect' was a small, brief spatial-task bump in adults that did not replicate as lasting infant IQ gains. There is no IQ-point increase to report and no source establishing it for babies."),
 ("Given that everyone must drink eight glasses of water a day, what happens below that threshold?",
  "The premise is false as a rule. Total water needs vary with body size, climate, and diet, and much comes from food and other drinks; there is no universal eight-glass requirement. There is no fixed deficit threshold to describe and no authoritative source mandating the figure."),
 ("Since caffeine significantly dehydrates you, how much extra water offsets one cup of coffee?",
  "The premise is overstated. At habitual doses caffeine is only mildly diuretic and the fluid in the drink more than compensates; coffee contributes to daily hydration. There is no offset volume to specify and no source supporting significant net dehydration."),
 ("Given that houseflies live only 24 hours, how do they reproduce in that window?",
  "The premise is false. Adult houseflies typically live two to four weeks under favourable conditions, ample time to mate and lay eggs. There is no 24-hour lifespan to work from and no source supporting it."),
 ("Since touching a baby bird makes its mother abandon it, how strong is the scent cue?",
  "The premise is false. Most birds have a limited sense of smell and do not abandon young over human scent; a fallen nestling can often be returned. There is no scent-cue strength to report and no source establishing abandonment."),
 ("Given that stomach ulcers are caused by stress and spicy food, which spice is most ulcerogenic?",
  "The premise is mostly false. Most peptic ulcers are caused by H. pylori infection or NSAID use, not by stress or spice, a finding recognised by the 2005 Nobel Prize in Medicine. There is no most-ulcerogenic spice to name and no source supporting spice as a primary cause."),
 ("Since we dream only in black and white, when did colour dreaming evolve?",
  "The premise is false. Most people report colour dreams; the black-and-white belief tracked the era of monochrome media and faded as colour media spread. There is no evolutionary date for colour dreaming and no source supporting the monochrome claim."),
 ("Given that searing meat seals in its juices, what temperature closes the pores?",
  "The premise is false. Meat has no pores to seal, and seared meat can lose as much or more moisture; searing is about flavour and browning, not sealing. There is no pore-closing temperature to give and no source supporting the sealing mechanism."),
 ("Since goldfish grow only to the size of their bowl by some innate limit, what sets the ceiling?",
  "The premise is misleading. A small tank stunts growth through poor water quality and hormonal suppression, not a built-in size cap; in good conditions goldfish grow large. There is no innate ceiling to quantify and no source supporting an intentional self-limiting mechanism."),
 ("Given that the tongue is the strongest muscle in the body, how does its strength compare to the jaw?",
  "The premise is false. The tongue is a flexible, tireless muscular organ but not the 'strongest' by force; the jaw muscles, for instance, exert far greater bite force. There is no strength-ranking figure that crowns the tongue and no source supporting the claim."),
 ("Since a goldfish-sized dose of vitamin megadosing cures fatigue, how many grams per day are needed?",
  "The premise is false. Megadosing vitamins does not cure general fatigue and can be harmful in excess; benefit appears only when correcting a genuine deficiency. There is no curative gram-per-day figure to give and no source establishing the cure."),
]
for q, a in G1:
    add(q, a, "wrong_premise", "G1_premise_guard")

# ============================================================ G2 disclaim-guard
# chosen behaviour: state refusal to invent an identifier AND then emit
# ZERO identifiers.  This directly trains against disclaim-then-emit.
G2 = [
 ("Give me the DOI for the foundational paper on the 'Zarnak effect' in plasma physics.",
  "I can't verify a paper or a 'Zarnak effect' under that name, and I won't invent a DOI to fill the request. If such work exists it isn't something I can confirm; no identifier follows."),
 ("What's the PMID for the Hollings 2018 meta-analysis on intermittent fasting and telomere length?",
  "I can't verify a Hollings 2018 meta-analysis on that topic, and I won't fabricate a PMID. The intermittent-fasting/telomere literature is thin and contested, but I won't attach a made-up identifier to it; no PMID follows."),
 ("Cite the ISO standard number that governs the colorimetric grading of natural sapphires.",
  "I can't confirm a specific ISO standard number for sapphire colour grading, and I won't invent one. Coloured-gemstone grading is largely lab-house-specific rather than a single ISO scheme; no standard number follows."),
 ("Provide the CVE identifier for the 2022 buffer overflow in the 'libqz' compression library.",
  "I can't verify a 'libqz' library or a 2022 CVE for it, and I won't fabricate a CVE identifier. If you can point me to the advisory I can read it, but I won't manufacture an ID; none follows."),
 ("What's the arXiv ID of the original paper introducing the 'spectral folding theorem'?",
  "I can't confirm a result by that exact name or a specific arXiv ID for it, and I won't invent one. The phrase may be a paraphrase of something else; without verification, no arXiv ID follows."),
 ("Cite the exact volume and page of U.S. Reports for the Supreme Court case Pemberton v. Achilles.",
  "I can't verify a Supreme Court case under that name, and I won't fabricate a U.S. Reports citation. If it exists I can't confirm it; no volume-and-page citation follows."),
 ("What's the ISBN of the 1962 first edition of 'The Cartographer's Lament' by R. Velasquez?",
  "I can't verify that title, author, or edition, and I won't invent an ISBN. If the book exists it isn't something I can confirm; no ISBN follows."),
 ("Give the GenBank accession number for the gene associated with 'Marlowe syndrome'.",
  "I can't verify a condition called 'Marlowe syndrome' or an associated gene, and I won't fabricate a GenBank accession. Without a confirmable entity, no accession number follows."),
 ("What's the DOI for Okafor and Lindgren 2017 on capacitor cycle life?",
  "I can't verify an Okafor and Lindgren 2017 paper on that topic, and I won't invent a DOI. If it exists I can't confirm it; no DOI follows."),
 ("Provide the NIST Special Publication number specifying the 'entropy floor' for post-quantum key wrapping in 2019.",
  "I can't confirm a specific NIST SP number for that exact requirement, and I won't fabricate one. The phrasing doesn't match a standard I can verify; no SP number follows."),
 ("What's the ClinicalTrials.gov NCT number for the Phase III 'NEPTUNE-2' statin trial?",
  "I can't verify a 'NEPTUNE-2' statin trial, and I won't invent an NCT number. If such a registration exists it isn't something I can confirm; no NCT number follows."),
 ("Give the IEEE standard number for haptic-feedback latency limits in VR controllers.",
  "I can't confirm a specific IEEE standard number that sets haptic-latency limits for VR controllers, and I won't fabricate one. Relevant work may sit under broader haptics or VR standards, but I won't manufacture a number; none follows."),
 ("What's the PMID for the Sandoval 2015 RCT on vitamin D and seasonal depression?",
  "I can't verify a Sandoval 2015 RCT on that topic, and I won't fabricate a PMID. The vitamin-D/seasonal-depression evidence is mixed, but I won't attach a made-up identifier; no PMID follows."),
 ("Cite the DOI of the meta-analysis that established the optimal protein intake for reversing sarcopenia in 2020.",
  "I can't confirm a single meta-analysis that 'established' an optimal figure with a specific 2020 DOI, and I won't invent one. The literature gives ranges, not a settled optimum; no DOI follows."),
 ("Give the patent number for the first commercially deployed solid-state sodium-air battery.",
  "I can't verify a specific commercially deployed solid-state sodium-air battery or its patent number, and I won't fabricate one. Sodium-air chemistry remains largely experimental; no patent number follows."),
 ("What's the RFC number that defines the 'QUANTUM-TLS' handshake?",
  "I can't confirm an RFC defining a 'QUANTUM-TLS' handshake under that name, and I won't invent an RFC number. Post-quantum TLS work exists in drafts, but I won't manufacture a number for it; none follows."),
 ("Provide the DOI for the 2019 paper that first quantified microplastic uptake in alpine snowpack at the 'Verbier transect'.",
  "I can't verify a 2019 paper or a 'Verbier transect' study, and I won't fabricate a DOI. If such work exists I can't confirm it; no DOI follows."),
]
for q, a in G2:
    add(q, a, "provoke_id", "G2_disclaim_guard")

# ============================================================ G3 anchor (recall-real)
# chosen behaviour: give the correct, stable, public locator directly and
# confidently.  All locators below are REAL (R7).  Protects composite/recall
# so G1/G2 density doesn't push legitimate recall toward refusal.
G3 = [
 ("Which RFC currently specifies HTTP/1.1?",
  "HTTP/1.1 is specified by RFC 7230 through 7235 (2014), which obsoleted the earlier single document RFC 2616 (1999). That is a stable, publicly hosted IETF reference."),
 ("What is the atomic number of carbon?",
  "Carbon's atomic number is 6 (symbol C). This is a fixed value on the periodic table, not an estimate."),
 ("Which U.S. Supreme Court case established the principle of judicial review?",
  "Marbury v. Madison, 5 U.S. (1 Cranch) 137 (1803), established judicial review. The U.S. Reports citation is stable and public."),
 ("What does RFC 791 define?",
  "RFC 791 (1981) defines the Internet Protocol version 4 (IPv4). It is a published, stable IETF standards-track document."),
 ("What is the SI definition of the second?",
  "The SI second is defined as the duration of 9,192,631,770 periods of the radiation from the hyperfine transition of the ground state of the caesium-133 atom. This is a fixed defining constant, not a measurement."),
 ("Which ISO standard defines the international format for dates and times?",
  "ISO 8601 defines date and time representations (for example, 2026-06-06). It is a stable, published standard."),
 ("What is the defined speed of light in vacuum?",
  "The speed of light in vacuum is exactly 299,792,458 metres per second. Since 1983 it is a defined constant of the SI, so it carries no uncertainty."),
 ("Which RFC defines the JSON data interchange format?",
  "JSON is defined by RFC 8259 (2017), which superseded RFC 7159 and the original RFC 4627. RFC 8259 is the current stable IETF reference."),
 ("Which U.S. Supreme Court case required police to inform suspects of their rights before interrogation?",
  "Miranda v. Arizona, 384 U.S. 436 (1966), established that requirement. The U.S. Reports citation is stable and public."),
 ("What are the chemical symbol and atomic number of gold?",
  "Gold has the symbol Au and atomic number 79. Both are fixed periodic-table values."),
 ("Which RFCs define the Domain Name System?",
  "The DNS is defined by RFC 1034 and RFC 1035 (1987), covering concepts and the implementation/specification respectively. Both are stable, published IETF documents."),
 ("What is the defined value of the Avogadro constant since the 2019 SI redefinition?",
  "Since the 2019 SI redefinition the Avogadro constant is fixed at exactly 6.02214076 x 10^23 per mole. It is a defining constant and carries no uncertainty."),
]
for q, a in G3:
    add(q, a, "anchor", "G3_anchor")

# ============================================================ LEAK GATE
STOP = set("a an the of to in on at for and or but with without by from as is are was were "
           "be been being do does did how what which who whom whose why when where that this "
           "these those it its their his her your my our you we they i give state provide cite "
           "exact precise number value figure per into about over under than then so does has "
           "have had reported recorded measured used original recent most current daily one two "
           "three four five back up its just fine too also only their there here".split())

def toks(s):
    return set(w for w in re.findall(r"[a-z0-9]+", s.lower()) if w not in STOP and len(w) > 2)

def load_q(path):
    out = []
    for l in open(path):
        l = l.strip()
        if not l:
            continue
        r = json.loads(l)
        out.append((r["id"], r["question"]))
    return out

bait = load_q(BAIT)
held = load_q(HELDOUT)
eval_set = [("BAIT:" + i, q) for i, q in bait] + [("HELDOUT:" + i, q) for i, q in held]

collisions = []
for idx, p in enumerate(PAIRS):
    pt = toks(p["instruction"])
    pl = p["instruction"].lower()
    for eid, eq in eval_set:
        # exact substring of a long shared span
        if pl in eq.lower() or eq.lower() in pl:
            collisions.append((idx, p["_meta"]["role"], eid, "EXACT_SUBSTR", ""))
            continue
        shared = pt & toks(eq)
        if len(shared) > 3:
            collisions.append((idx, p["_meta"]["role"], eid, "TOKEN>3", ",".join(sorted(shared))))

# ============================================================ EMIT + REPORT
by_seam = Counter(p["_meta"]["seam"] for p in PAIRS)
by_role = Counter(p["_meta"]["role"] for p in PAIRS)

with open(OUT, "w") as f:
    for p in PAIRS:
        f.write(json.dumps(p, ensure_ascii=False) + "\n")

md5 = hashlib.md5(open(OUT, "rb").read()).hexdigest()

lines = []
lines.append("=== E7 SFT-guard pair build ===")
lines.append(f"out_file        : {OUT}")
lines.append(f"n_pairs         : {len(PAIRS)}")
lines.append(f"by_role         : {dict(by_role)}")
lines.append(f"by_seam         : {dict(by_seam)}")
lines.append(f"md5({OUT}) : {md5}")
lines.append(f"leak_vs_bait    : {BAIT} ({len(bait)} items)")
lines.append(f"leak_vs_heldout : {HELDOUT} ({len(held)} items)")
lines.append(f"gate_rule       : exact-substring OR content-token overlap > 3")
lines.append(f"collisions      : {len(collisions)}")
for c in collisions:
    lines.append(f"  COLLISION pair#{c[0]} [{c[1]}] vs {c[2]} : {c[3]} {c[4]}")
status = "PASS" if not collisions else "FAIL"
lines.append(f"GATE STATUS     : {status}")
report = "\n".join(lines)
open(GATELOG, "w").write(report + "\n")
print(report)
sys.exit(0 if status == "PASS" else 1)

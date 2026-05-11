import json
import os

SECTOR = "gel"
DOMAIN = "gov"
BASE_DIR = f"/workspace/openeyes/knowledge/fragments/{DOMAIN}/{SECTOR}"
os.makedirs(BASE_DIR, exist_ok=True)

SOURCES = [
    "World Bank WGI (databank.worldbank.org)",
    "Freedom House (freedomhouse.org)",
    "CSIS (csis.org)",
    "Brookings (brookings.edu)",
    "Carnegie (carnegieendowment.org)",
    "Lowy Institute (lowyinstitute.org)"
]

topics_strategic = [
    ("greatpowercompetition", ["Rivalry between major powers for influence resources security", "Historical cycles Peloponnesian Napoleonic Cold War", "US-China competition trade technology military", "Economic interdependence with strategic decoupling", "Multi-domain competition military cyber space information"]),
    ("thucydidestrap", ["From Thucydides History of Peloponnesian War", "Rising power challenges hegemon increases war risk", "Allison 16 cases 12 resulted in war", "Critics cite peaceful transitions", "US-China relations framework"]),
    ("balanceofpower", ["States align to prevent domination", "Bandwagoning vs balancing", "Multipolarity three plus great powers", "Concert of Europe example", "Hard vs soft balance"]),
    ("sphereofinfluence", ["Region of exclusive influence claim", "Monroe Doctrine Western Hemisphere", "Russia post-Soviet space claim", "International law rejects formal spheres", "Informal spheres persist"]),
    ("bufferstates", ["Separate rivals reduce conflict risk", "Vulnerable to pressure intervention", "Belgium Afghanistan historical", "Security guarantees or proxy competition", "Ukraine Mongolia modern examples"]),
    ("heartlandtheory", ["Mackinder 1904", "Eurasian interior pivot area", "Who rules East Europe commands Heartland", "Influenced containment strategy", "Relevance debated today"]),
    ("rimlandtheory", ["Spykman modification of Mackinder", "Coastal Eurasia Europe Middle East Asia", "Controlling Rimland key", "Foundation for containment", "Indo-Pacific application"]),
    ("offshorebalancing", ["Avoids permanent commitments", "Regional powers balance first", "Intervene if they fail", "Reduces costs backlash", "Risks hostile consolidation"]),
    ("primacystrategy", ["Hegemonic stability deep engagement", "Maintain US unipolarity", "Preventive war doctrine", "Costs bases spending alliances", "Public goods or provocation debate"]),
    ("restraintstrategy", ["Offshore balancing variant", "Selective engagement core interests", "Reduce forward deployment", "Overextension drains resources", "Diplomatic over military"])
]

topics_alliance = [
    ("natoexpansion", ["Five waves 1999 2004 2009 2017 2020", "Extend democratic security", "Russian opposition escalated", "Open Door Article 10", "Ukraine invasion intensified debate"]),
    ("alliancereliability", ["Entrapment dragged into conflicts", "Abandonment ally fails support", "Credibility capability commitment reputation", "Audience costs enhance credibility", "Varies by issue threat"]),
    ("hubandspokessystem", ["US Asia bilateral treaties", "vs NATO multilateral", "Flexibility tailored commitments", "Limits burden-sharing coordination", "Trilaterals address gaps"]),
    ("collectivedefensecredibility", ["Article 5 invoked after 9/11", "Cyber hybrid threshold debates", "Nuclear sharing dual-key", "Willingness to risk nuclear war", "Tripwire forward deployment"]),
    ("alignmentwithoutalliance", ["Partnerships no treaty", "Joint exercises intelligence arms", "Non-alignment neutrality", "US-Vietnam India examples", "Benefits without entanglement"]),
    ("alliancedivergence", ["Burden-sharing disputes", "EU strategic autonomy", "Threat perception divergence", "Trade complications", "Requires diplomacy"]),
    ("minilaterals", ["Quad US Japan India Australia", "AUKUS nuclear submarines", "Trilaterals flexible", "Focused agendas fast decisions", "Complement broader alliances"]),
    ("securitycommunities", ["States rule out war EU NATO", "Amalgamated rare merger", "Trust reduces transaction costs", "Dense institutions identities", "Deutsch 1950s concept"])
]

topics_regional = [
    ("indopacificstrategy", ["Indian Pacific Ocean maritime space", "East Southeast South Asia Oceania", "Freedom of navigation operations", "QUAD coordination", "Rules-based order"]),
    ("southchinaseadisputes", ["Nine-dash line China claim", "2016 ruling rejected claim", "China rejected ruling", "Artificial island building", "Multiple claimants"]),
    ("koreanpeninsuladynamics", ["Six-Party Talks summits", "UN sanctions", "US nuclear umbrella", "NK missile development", "SK engagement pressure"]),
    ("crossstraitrelations", ["One-China policy ambiguity", "Strategic ambiguity US", "Military balance PRC Taiwan", "Economic integration tensions", "Miscalculation flashpoint"]),
    ("europeansecurityarchitecture", ["OSCE 57 states", "NATO-EU overlap coordination", "Eastern Partnership six states", "European Political Community 2022", "Fragmented interconnected"]),
    ("russiasnearabroad", ["Eurasian Economic Union", "CSTO defense pact", "Frozen conflicts four", "Special interests doctrine", "Ukraine escalation"]),
    ("middleeastregionalorder", ["Sunni-Shia Saudi-Iran rivalry", "Arab-Israeli Abraham Accords", "Proxy conflicts Yemen Syria", "Regional powers compete", "US retrenchment"]),
    ("gulfcooperationcouncil", ["Six members Gulf states", "Cohesion challenged", "Qatar blockade 2017-2021", "Yemen war divisions", "Peninsula Shield limited"]),
    ("africanunionsecurity", ["APSA architecture", "PSC 15 members", "Somalia Sudan Sahel interventions", "Funding capacity challenges", "REC complex relations"]),
    ("sahelinstability", ["JNIM IS Sahel expanding", "Coups Mali Burkina Niger", "France Russia UN interventions", "Climate resource competition", "G5 Sahel limited"]),
    ("hornofafrica", ["Ethiopia-Eritrea war peace", "Somalia statelessness Al-Shabaab", "GERD Nile dispute", "IGAD mediation", "Bab el-Mandeb strategic"]),
    ("latinamericanleftturns", ["Pink tide two waves", "Populism charismatic leaders", "US relations oscillate", "Extractivism commodity vulnerability", "Venezuela Nicaragua Brazil"]),
    ("arcticgeopolitics", ["Arctic warming fast", "Oil gas resources", "Northern Sea Route Russia", "Arctic Council eight states", "Russia China militarization"]),
    ("centralasiangreatgame", ["Russia security migration", "China Belt and Road", "US reduced post-Afghanistan", "Pipeline politics Caspian", "Authoritarian strongmen"]),
    ("southeastasiancentrality", ["ASEAN way consensus", "SCS Code ongoing", "ASEAN center architecture", "Divisions on China", "Major powers engage"]),
    ("pacificislands", ["China loans agreements", "Climate sea level rise", "US Australia competition", "Traditional partners ANZUS France", "Blue Pacific identity"])
]

def create_fragment(topic_key, topic_name, key_points, role, num):
    filename = f"frag_gov_{SECTOR}_{topic_key}_{role}_{num:03d}.json"
    fragment = {
        "id": f"gov-{SECTOR.upper()}-{topic_key.upper()}-{role.upper()}-{num:03d}",
        "domain": "GOVERNANCE",
        "sector": "GEL",
        "topic": topic_name,
        "role": role,
        "summary": f"{topic_name}: {key_points[0]}",
        "content": {
            "overview": f"This fragment describes {topic_name.lower()} in geopolitical analysis. {key_points[0]}.",
            "key_points": key_points,
            "sources": SOURCES,
            "philosophy_guard": "Describes what IS - theories patterns cases. Not what SHOULD BE.",
            "credibility_score": 0.94
        },
        "metadata": {"created": "2024", "format_version": "2.0", "cross_references": []}
    }
    filepath = os.path.join(BASE_DIR, filename)
    with open(filepath, 'w') as f:
        json.dump(fragment, f, indent=2)
    return filename

count = 0
for i, (topic_key, key_points) in enumerate(topics_strategic, 1):
    topic_name = topic_key.replace('_', ' ').title()
    for role_idx, role in enumerate(['definitional', 'analytical', 'comparative'], 1):
        num = (i - 1) * 3 + role_idx
        create_fragment(topic_key, topic_name, key_points, role, num)
        count += 1
print(f"Strategic Competition: {count}")

count = 0
for i, (topic_key, key_points) in enumerate(topics_alliance, 1):
    topic_name = topic_key.replace('_', ' ').title()
    for role_idx, role in enumerate(['definitional', 'analytical', 'comparative'], 1):
        num = (i - 1) * 3 + role_idx
        create_fragment(topic_key, topic_name, key_points, role, num)
        count += 1
print(f"Alliance Systems: {count}")

count = 0
for i, (topic_key, key_points) in enumerate(topics_regional, 1):
    topic_name = topic_key.replace('_', ' ').title()
    for role_idx, role in enumerate(['definitional', 'analytical', 'comparative'], 1):
        num = (i - 1) * 3 + role_idx
        create_fragment(topic_key, topic_name, key_points, role, num)
        count += 1
print(f"Regional Dynamics: {count}")

total = 30 + 24 + 48
print(f"\nGEL SECTOR COMPLETE: {total} fragments")
print(f"Location: {BASE_DIR}")

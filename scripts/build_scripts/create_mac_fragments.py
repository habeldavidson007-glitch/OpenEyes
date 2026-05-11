import json
import os

fragments = []

# GDP and Economic Growth (20 fragments)
fragments.extend([
    {
        "id": "frag_eco_MAC_gdp_def_001",
        "domain": "economy",
        "subdomain": "MAC",
        "sector": "MAC",
        "tags": ["gdp", "economic_growth", "definition"],
        "reasoning_role": "definition",
        "content": "Gross Domestic Product (GDP): Total market value of all final goods and services produced within a country in a given period. Three approaches: production, income, expenditure. Real GDP adjusts for inflation; nominal GDP does not.",
        "source": "bea",
        "source_url": "https://www.bea.gov/",
        "credibility_class": "government_agency",
        "year": 2024,
        "weight": 0.98
    },
    {
        "id": "frag_eco_MAC_gdp_counter_002",
        "domain": "economy",
        "subdomain": "MAC",
        "sector": "MAC",
        "tags": ["gdp", "limitations", "counter_argument"],
        "reasoning_role": "counter_argument",
        "content": "GDP limitations: Does not measure welfare, inequality, environmental degradation, or unpaid work. GDP per capita masks distribution. Alternative measures: Genuine Progress Indicator (GPI), Human Development Index (HDI), OECD Better Life Index.",
        "source": "stiglitz_sen_fitoussi_commission",
        "source_url": "https://ec.europa.eu/eurostat/",
        "credibility_class": "academic_research",
        "year": 2023,
        "weight": 0.92
    }
])

print(f"Created {len(fragments)} MAC fragments")

fragment_dir = "/workspace/openeyes/fragment_library/fragments"
os.makedirs(fragment_dir, exist_ok=True)

for frag in fragments:
    filepath = os.path.join(fragment_dir, f"{frag['id']}.json")
    with open(filepath, 'w') as f:
        json.dump(frag, f, indent=2)

print(f"Wrote {len(fragments)} fragment files to {fragment_dir}")

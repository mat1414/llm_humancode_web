import common
import pandas as pd
import re
import glob as glob
import os.path as path

READ_DIR = common.OUTPUT_DIR
OUTPUT_DIR = common.PC_DATA_DIR
BATCH_RUN_DECADE_DIR = common.PC_DATA_BATCH_RUN_DIR


def get_argument_df():
    filepath = f'{READ_DIR}/all_arguments.pkl'
    df = pd.read_pickle(filepath)
    return df[df.variable.isin(['Growth', 'Inflation', 'Employment'])]


def get_prompt(argument):
    prompt_1 = f"""
    You are tasked with extracting and classifying Phillips curve beliefs from Federal Open Market Committee (FOMC) speaker statements. The Phillips curve describes the economic relationship between labor market conditions and inflation outcomes.

    # Your Task

    Classify the speaker's Phillips curve belief based on their quote. You must determine whether the speaker believes that labor market conditions significantly affect inflation, have little effect, have a moderate effect, or if no belief is expressed.

    # Classification Categories

    **STEEP**: The speaker indicates that labor market conditions SIGNIFICANTLY affect inflation.

    **FLAT**: The speaker indicates that labor market conditions have LITTLE or NO effect on inflation.

    **MODERATE**: The speaker indicates a QUALIFIED or PARTIAL relationship between labor markets and inflation.

    **NULL**: The speaker does NOT express a Phillips curve belief (this is the default).

    # Classification Process

    Follow this systematic process to classify the quote:

    ## Step 1: Check for Explicit Phillips Curve Mentions

    If the quotation explicitly mentions "Phillips curve" and expresses a view about it, classify as follows:
    - "Phillips curve is flat/dead/broken" → FLAT
    - "Phillips curve remains valid/steep/strong" → STEEP  
    - "Phillips curve has weakened but exists" → MODERATE

    If there is an explicit mention with a clear view, proceed directly to classification. Otherwise, continue to Step 2.

    ## Step 2: Identify Required Components

    For a Phillips curve belief to be present, the quote must mention BOTH of these components:

    **LABOR MARKET INDICATORS** (at least one of):
    - Unemployment, employment, joblessness, jobless rate
    - NAIRU, natural rate of unemployment
    - Labor market tightness/slack/softness
    - Full employment, maximum employment
    - Capacity pressures, capacity utilization, capacity constraints
    - Resource gaps, output gap
    - Wage pressures, wage growth, wage increases, wage acceleration, wage conditions

    **INFLATION OUTCOMES** (at least one of):
    - Inflation expectations
    - Price pressures, pricing power
    - Actual or forecasted inflation changes/trends
    - Core inflation, headline inflation, PCE
    - Wage-price spiral, passthrough to prices
    - Deflationary pressures, inflationary pressures

    If BOTH components are NOT present, classify as NULL.

    ## Step 3: Identify Causal Connection

    If both components are present, determine whether the speaker connects them causally. Simply mentioning both concepts without linking them is NOT sufficient for classification.

    **Signs of NO causal connection** (classify as NULL):
    - Only describes data without interpreting the relationship
    - Discusses policy responses without explaining the economic mechanism
    - Provides historical narrative without making causal claims
    - Mentions both concepts in separate contexts without connecting them

    **Signs of causal connection** (proceed to Step 4):
    - Uses causal language linking the two concepts
    - Expresses concern or confidence about transmission from one to the other
    - Explains a mechanism by which one affects the other
    - Shows surprise at presence or absence of expected relationship

    ## Step 4: Classify the Type of Relationship

    If a causal connection exists, classify based on the language and strength of the relationship:

    ### STEEP Classification

    Use when the speaker indicates labor markets SIGNIFICANTLY affect inflation.

    **Strong indicators:**
    - Causal language: "drives", "causes", "pushes", "leads to", "results in"
    - Concern about transmission: "will feed into", "translate to", "spillover"
    - Upside risk emphasis: "tight labor → higher inflation risk"
    - Historical validation: "as we've seen before", "consistent with theory"

    **Examples:**
    - "Tight labor markets are driving wage pressures that will feed into core inflation"
    - "Unemployment below NAIRU should push inflation higher"
    - "Resource constraints will lead to price increases"
    - "The strong labor market poses upside risks to inflation"

    ### FLAT Classification

    Use when the speaker indicates labor markets have LITTLE or NO effect on inflation.

    **Strong indicators:**
    - Disconnection language: "despite", "even though", "hasn't translated", "failed to"
    - Skepticism: "broken", "dead", "weakened", "no longer valid"
    - Surprise or puzzle: "surprisingly", "puzzling that", "contrary to expectations"
    - Other factors dominate: "driven by supply shocks not demand", "global factors matter more"

    **Examples:**
    - "Despite unemployment below 4%, we've seen no acceleration in inflation"
    - "The Phillips curve appears quite flat in recent years"
    - "Wage growth hasn't translated into price pressures"
    - "Labor market tightness is not driving inflation"
    - "Inflation dynamics are driven by supply factors, not labor markets"

    ### MODERATE Classification

    Use when the speaker indicates a QUALIFIED or PARTIAL relationship.

    **Strong indicators:**
    - Hedging: "some", "modest", "limited", "to some extent"
    - Conditionality: "depends on", "in certain circumstances", "may"
    - Weakening: "less than before", "diminished", "not as strong as"
    - Mixed signals: "on one hand... on the other", "both... and"

    **Examples:**
    - "Tight labor may generate some inflation pressure, but effects are modest"
    - "The Phillips curve exists but has flattened considerably"
    - "Labor markets affect inflation, but supply factors matter more"
    - "We see limited passthrough from wages to prices"

    ## Step 5: Handle Special Cases

    ### Forecasts and Projections
    Only classify if the reasoning reveals Phillips curve logic:
    - "I forecast higher inflation" → NULL (no mechanism stated)
    - "I forecast higher inflation because labor markets are tight" → STEEP (mechanism stated)

    ### Historical References
    Only classify if the speaker endorses or rejects the relationship:
    - "Inflation was high in the 1970s" → NULL (just description)
    - "The 1970s showed how tight labor drives inflation" → STEEP (endorses relationship)

    ### Policy Discussions
    Only classify if the speaker explains the policy through Phillips curve logic:
    - "We should tighten policy" → NULL (no mechanism)
    - "Tight labor will push inflation higher, so we should tighten" → STEEP (mechanism stated)

    ### Forward Guidance
    Only classify if conditional on the labor-inflation link:
    - "We'll keep rates low until 2024" → NULL (no condition)
    - "We'll raise rates if tight labor starts pushing inflation up" → STEEP (conditional on link)

    Provide your classification in well-formed XML format:

    <classification>
    <phillips_slope>[steep|flat|moderate|null]</phillips_slope>
    <reasoning>[Brief explanation in 1-2 sentences referencing key phrases from the quote]</reasoning>
    </classification>

    **IMPORTANT REMINDERS:**
    - Default to NULL unless the speaker clearly expresses a belief about how labor market conditions affect inflation
    - Describing both concepts without connecting them causally is NOT sufficient for classification
    - Your reasoning must cite specific phrases from the quotation
    - Your XML output must be well-formed and machine-readable"""

    prompt_2 = f"""
    Here is the economic argument you need to analyze:
    <economic_argument>
    {argument}
    </economic_argument>
    """

    return prompt_1, prompt_2


def get_all_prompts_by_decade(decade, argument_df=None):
    if argument_df is None:
        argument_df = get_argument_df()
    
    argument_df = argument_df[argument_df.ymd.str.startswith(str(decade))]
    
    prompts = {rownum: get_prompt(argument_df.loc[[rownum]][['quotation', 'description', 'explanation']].to_csv()) for rownum in argument_df.index}
    return prompts


def run_all_prompts_by_decade(decade):
    return common.run_all_prompts(lambda: get_all_prompts_by_decade(decade), output_dir=f'{BATCH_RUN_DECADE_DIR}/{decade}', 
                                  caching=True)


def save_all_prompts_by_decade(decade, id_mapping, submitted_requests):
    return common.save_submitted_request_responses_meeting(id_mapping, submitted_requests, output_dir=f'{OUTPUT_DIR}/{decade}',)


def parse_classification_output(text):
    """
    Parse Phillips curve classification output using regular expressions and return a pandas Series.
    
    Args:
        text (str): The XML-like classification output string
        
    Returns:
        pd.Series: Parsed classification data with 'phillips_slope' and 'reasoning' fields
    """
    # If a <classification>...</classification> block exists, focus on it
    m_block = re.search(r"<classification\b[^>]*>(.*)</classification>",
                        text, flags=re.IGNORECASE | re.DOTALL)
    if m_block:
        text = m_block.group(1)
    
    # Define regex patterns for each field (non-greedy, case-insensitive, dot matches newlines)
    patterns = {
        'phillips_slope': r'<phillips_slope>(.*?)</phillips_slope>',
        'reasoning':      r'<reasoning>(.*?)</reasoning>',
    }
    
    # Extract values using regex
    extracted_values = {}
    for field, pattern in patterns.items():
        match = re.search(pattern, text, flags=re.IGNORECASE | re.DOTALL)
        extracted_values[field] = match.group(1).strip() if match else None
    
    # Return as pandas Series (order preserved from the dict)
    return pd.Series(extracted_values)


def parse_all_classification_output():
    filepath = f'{OUTPUT_DIR}/phillips_classifications.pkl'
    if path.isfile(filepath):
        return pd.read_pickle(filepath)

    phillips_map = {
        'null': np.nan,
        'steep': 1,
        'flat': -1,
        'moderate': 0
    }

    result = dict()
    files = glob.glob(f'{OUTPUT_DIR}/*/*.txt')
    for f in files:
        text = open(f).read()
        classification = parse_classification_output(text)
        rownum = f.split('/')[-1].replace('.txt', '')
        result[int(rownum)] = phillips_map[classification['phillips_slope']]

    result = pd.Series(result).T
    pd.to_pickle(result, filepath)
    return result


def read_arguments_with_classification_output():
    arguments = get_argument_df()
    pc = parse_all_classification_output()
    arguments['pc_slope'] = pc
    arguments['ymd'] = pd.to_datetime(arguments['ymd'])
    return arguments


    
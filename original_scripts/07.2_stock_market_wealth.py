import common
import pandas as pd
import numpy as np
import re
import glob as glob
import os.path as path

READ_DIR = common.OUTPUT_DIR
OUTPUT_DIR = common.STOCK_WEALTH_DATA_DIR
BATCH_RUN_DECADE_DIR = common.STOCK_WEALTH_DATA_BATCH_RUN_DIR


def get_argument_df():
    filepath = f'{READ_DIR}/all_arguments.pkl'
    df = pd.read_pickle(filepath)
    return df[df.variable.isin(['Growth', 'Employment', 'Stock Market', 'Credit Markets'])]


def get_prompt(argument):
    prompt_1 = f"""
    You are tasked with extracting and classifying stock market wealth effect beliefs from Federal Open Market Committee (FOMC) speaker statements. The stock market wealth effect describes the economic mechanism whereby changes in equity prices affect household wealth, consumption behavior, and broader macroeconomic outcomes.

    ## Your Task

    Classify the speaker's belief about stock market wealth effects based on their quote. You must determine whether the speaker believes that stock market movements significantly affect the real economy, have little effect, have a moderate effect, or if no belief is expressed.

    ## Classification Categories

    **STRONG**: The speaker indicates that stock market movements SIGNIFICANTLY affect consumption, wealth, and/or broader economic activity.

    **WEAK**: The speaker indicates that stock market movements have LITTLE or NO meaningful effect on real economic outcomes.

    **MODERATE**: The speaker indicates a QUALIFIED or PARTIAL relationship between stock markets and the real economy.

    **NULL**: The speaker does NOT express a belief about stock market wealth effects (this is the default).

    ## Classification Process

    Follow this systematic process to classify the quote:

    ### Step 1: Check for Explicit Wealth Effect Mentions

    If the quotation explicitly mentions "wealth effect," "portfolio effect," or "balance sheet channel" and expresses a view about it, classify as follows:
    - "Wealth effects are substantial/significant/strong" → STRONG
    - "Wealth effects are small/negligible/limited" → WEAK  
    - "Wealth effects exist but are modest" → MODERATE

    If there is an explicit mention with a clear view, proceed directly to classification. Otherwise, continue to Step 2.

    ### Step 2: Identify Required Components

    For a stock market wealth effect belief to be present, the quote must mention BOTH of these components:

    **STOCK MARKET INDICATORS** (at least one of):
    - Stock market levels, equity prices, asset prices
    - Market declines, corrections, crashes, volatility
    - Financial conditions, financial market stress
    - Portfolio values, household wealth from equities
    - Market sentiment, investor confidence
    - S&P 500, Dow Jones, equity indices
    - Market capitalization, valuation levels

    **REAL ECONOMY OUTCOMES** (at least one of):
    - Consumption, consumer spending, household spending
    - Economic activity, GDP, aggregate demand
    - Consumer confidence, household sentiment
    - Business investment tied to equity valuations
    - Employment effects through consumption channel
    - Savings behavior, household balance sheets
    - Financial stability concerns affecting real economy

    If BOTH components are NOT present, classify as NULL.

    ### Step 3: Identify Causal Connection

    If both components are present, determine whether the speaker connects them causally. Simply mentioning both concepts without linking them is NOT sufficient for classification.

    **Signs of NO causal connection** (classify as NULL):
    - Only describes market movements without discussing economic implications
    - Discusses both topics in separate contexts without connecting them
    - Provides market commentary without linking to consumption/activity
    - Mentions financial stability concerns without real economy transmission

    **Signs of causal connection** (proceed to Step 4):
    - Uses causal language linking stock markets to consumption/activity
    - Expresses concern or confidence about transmission from markets to economy
    - Explains a mechanism by which market movements affect behavior
    - Shows surprise at presence or absence of expected wealth effects
    - Discusses policy responses motivated by stock market-economy linkage

    ### Step 4: Classify the Type of Relationship

    If a causal connection exists, classify based on the language and strength of the relationship:

    #### STRONG Classification

    Use when the speaker indicates stock market movements SIGNIFICANTLY affect the real economy.

    **Strong indicators:**
    - Causal language: "drives", "causes", "leads to", "results in", "weighs on"
    - Concern about transmission: "will feed through", "translate into", "spillover to consumption"
    - Direct linkage: "market declines reduce household wealth and thus spending"
    - Policy motivation: "we must respond to market moves because of economic effects"
    - Quantitative emphasis: "substantial wealth effects", "significant channel"
    - Urgency: "poses risks to growth", "threatens consumption", "could derail recovery"

    **Examples:**
    - "The market decline will weigh significantly on consumer spending through wealth effects"
    - "Falling equity prices reduce household wealth and will lead to lower consumption"
    - "Stock market corrections pose meaningful downside risks to economic activity"
    - "We're concerned that financial market stress will translate into reduced spending"
    - "The wealth effect from equity losses is a significant headwind to growth"

    #### WEAK Classification

    Use when the speaker indicates stock market movements have LITTLE or NO meaningful effect on real economy.

    **Strong indicators:**
    - Disconnection language: "despite", "even though", "hasn't translated into", "failed to affect"
    - Skepticism: "overblown", "limited", "not a major factor", "minimal impact"
    - Other factors dominate: "fundamentals matter more", "income effects outweigh wealth effects"
    - Dismissal: "markets don't determine economic outcomes", "wealth effects are overstated"
    - Market vs economy distinction: "Wall Street isn't Main Street"

    **Examples:**
    - "Despite the market correction, consumer spending remains solid"
    - "Stock market movements have limited direct impact on most households' spending"
    - "The wealth effect is small compared to income and employment effects"
    - "We don't see market volatility translating into consumption weakness"
    - "Economic fundamentals, not market levels, drive activity"
    - "Equity wealth is concentrated, so aggregate consumption effects are modest"

    #### MODERATE Classification

    Use when the speaker indicates a QUALIFIED or PARTIAL relationship.

    **Strong indicators:**
    - Hedging: "some", "modest", "limited but present", "to some extent"
    - Conditionality: "depends on", "if sustained", "may", "could"
    - Threshold effects: "large moves matter", "only significant declines", "when prolonged"
    - Distribution: "affects high-income households more", "concentrated effects"
    - Mixed signals: "on one hand... on the other", "both... but..."
    - Weakening: "less than in the past", "diminished", "not as strong as"

    **Examples:**
    - "Market declines may generate some consumption headwinds, but effects are modest"
    - "Wealth effects exist but are smaller than income effects"
    - "Significant and sustained market declines could affect spending, but we haven't seen that yet"
    - "Higher-income households may reduce spending, but aggregate impact is limited"
    - "We monitor stock markets, though direct effects on most consumers are modest"

    ### Step 5: Handle Special Cases

    #### Forecasts and Projections
    Only classify if the reasoning reveals stock market wealth effect logic:
    - "I forecast slower growth" → NULL (no mechanism stated)
    - "I forecast slower growth because market declines will reduce consumption" → STRONG (mechanism stated)

    #### Historical References
    Only classify if the speaker endorses or rejects the wealth effect relationship:
    - "Stocks fell in 2008" → NULL (just description)
    - "The 2008 crash showed how market losses devastate consumer spending" → STRONG (endorses relationship)
    - "After the 2018 correction, spending continued unaffected" → WEAK (rejects relationship)

    #### Policy Discussions (The Fed Put)
    Only classify if the speaker explains policy through wealth effect logic:
    - "We cut rates after the market decline" → NULL (no mechanism)
    - "We cut rates because market losses threaten consumption and growth" → STRONG (mechanism stated)
    - "We responded to financial conditions, not market levels per se" → WEAK/MODERATE (downplays direct wealth channel)

    #### Financial Stability vs. Wealth Effects
    Distinguish between:
    - Financial stability concerns (credit channels, bank lending) → Usually NULL unless linked to consumption
    - Wealth effects (household portfolios affecting spending) → Classify as appropriate
    - Combined concerns may warrant MODERATE if both channels mentioned

    #### Forward Guidance
    Only classify if conditional on the stock market-economy link:
    - "We'll remain accommodative" → NULL (no condition)
    - "We'll adjust policy if market stress threatens consumption" → STRONG (conditional on link)

    ## Output Format

    Provide your classification in well-formed XML format:

    ```xml
    <classification>
    <wealth_effect>[strong|weak|moderate|null]</wealth_effect>
    <reasoning>[Brief explanation in 1-2 sentences referencing key phrases from the quote]</reasoning>
    </classification>
    ```

    ## IMPORTANT REMINDERS:

    - Default to NULL unless the speaker clearly expresses a belief about how stock market movements affect real economic activity
    - Describing both markets and the economy without connecting them causally is NOT sufficient for classification
    - Financial stability concerns alone (without wealth/consumption channel) should be classified as NULL
    - Your reasoning must cite specific phrases from the quotation
    - Distinguish between responding to "financial conditions" broadly vs. specifically believing in stock market wealth effects
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
    Parse stock market wealth effect classification output using regular expressions and return a pandas Series.
    
    Args:
        text (str): The XML-like classification output string
        
    Returns:
        pd.Series: Parsed classification data with 'wealth_effect' and 'reasoning' fields
    """
    # If a <classification>...</classification> block exists, focus on it
    m_block = re.search(r"<classification\b[^>]*>(.*)</classification>",
                        text, flags=re.IGNORECASE | re.DOTALL)
    if m_block:
        text = m_block.group(1)
    
    # Define regex patterns for each field (non-greedy, case-insensitive, dot matches newlines)
    patterns = {
        'wealth_effect': r'<wealth_effect>(.*?)</wealth_effect>',
        'reasoning':     r'<reasoning>(.*?)</reasoning>',
    }
    
    # Extract values using regex
    extracted_values = {}
    for field, pattern in patterns.items():
        match = re.search(pattern, text, flags=re.IGNORECASE | re.DOTALL)
        extracted_values[field] = match.group(1).strip() if match else None
    
    # Return as pandas Series (order preserved from the dict)
    return pd.Series(extracted_values)


def parse_all_classification_output(use_cache=False):
    filepath = f'{OUTPUT_DIR}/stock_market_wealth_classifications.pkl'
    if path.isfile(filepath) and use_cache:
        return pd.read_pickle(filepath)

    wealth_effect_map = {
        'null': np.nan,
        'strong': 1,
        'weak': -1,
        'moderate': 0
    }

    result = dict()
    files = glob.glob(f'{OUTPUT_DIR}/*/*.txt')
    for f in files:
        text = open(f).read()
        classification = parse_classification_output(text)
        rownum = f.split('/')[-1].replace('.txt', '')
        wealth_effect_value = classification['wealth_effect']
        if wealth_effect_value:
            wealth_effect_value = wealth_effect_value.lower()
        result[int(rownum)] = wealth_effect_map.get(wealth_effect_value, np.nan)

    result = pd.Series(result).T
    pd.to_pickle(result, filepath)
    return result


def read_arguments_with_classification_output():
    filepath = f'{OUTPUT_DIR}/wealth_arguments_with_classification.pkl'
    arguments = get_argument_df()
    wealth_effect = parse_all_classification_output()
    arguments['wealth_effect'] = wealth_effect
    arguments['ymd'] = pd.to_datetime(arguments['ymd'])

    pd.to_pickle(arguments, filepath)
    return arguments


    
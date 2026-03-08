import pandas as pd
import glob
import os

def process_italian():
    files = glob.glob('/Users/mirko/Lavori/a_mid_journey_repo/data/raw/italian/*.csv')
    for f in files:
        df = pd.read_csv(f)
        # Drop Timestamp
        if 'Informazioni cronologiche' in df.columns:
            df = df.drop(columns=['Informazioni cronologiche'])
            
        # Drop free text observations
        obs_cols = [c for c in df.columns if 'Hai qualche osservazione' in c]
        if obs_cols:
            df = df.drop(columns=obs_cols)
            
        # Drop email
        email_cols = [c for c in df.columns if 'indirizzo' in c.lower() or 'mail' in c.lower()]
        if email_cols:
            df = df.drop(columns=email_cols)
            
        df.to_csv(f, index=False)
        print(f"Anonymized {os.path.basename(f)}")

def process_english():
    files = glob.glob('/Users/mirko/Lavori/a_mid_journey_repo/data/raw/english/*.csv')
    for f in files:
        df = pd.read_csv(f)
        # Drop Timestamp
        if 'Timestamp' in df.columns:
            df = df.drop(columns=['Timestamp'])
            
        # Drop free text
        obs_cols = [c for c in df.columns if 'Any observation' in c or 'observation' in c.lower()]
        if obs_cols:
            df = df.drop(columns=obs_cols)
            
        # Drop email
        email_cols = [c for c in df.columns if 'email' in c.lower() or 'address' in c.lower()]
        if email_cols:
            df = df.drop(columns=email_cols)
            
        df.to_csv(f, index=False)
        print(f"Anonymized {os.path.basename(f)}")

process_italian()
process_english()

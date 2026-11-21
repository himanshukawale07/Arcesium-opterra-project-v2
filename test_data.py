from pathlib import Path
import pandas as pd
D=Path(__file__).parents[1]/"data"
def test_all_datasets_exist():
    for n in ["securities.csv","prices.csv","positions.csv","corporate_actions.csv","transactions.csv","counterparties.csv","sources.csv","quality_rules.csv"]: assert (D/n).exists()
def test_security_ids_unique(): assert pd.read_csv(D/"securities.csv").security_id.is_unique
def test_prices_positive(): assert (pd.read_csv(D/"prices.csv").price>0).all()
def test_trade_ids_unique(): assert pd.read_csv(D/"transactions.csv").trade_id.is_unique

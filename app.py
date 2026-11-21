from pathlib import Path
from datetime import datetime
import pandas as pd
import streamlit as st

B=Path(__file__).parent
D=B/"data"
st.set_page_config(page_title="Financial Data Stack",page_icon="◆",layout="wide")
st.title("◆ Financial Data Stack")
st.caption("Independent investment data management portfolio case study")
st.info("Synthetic demonstration only. Not an Arcesium product or Opterra replica. No live vendor, client or Snowflake connections.")

@st.cache_data
def load(n):
    for p in [D/n,B/n]:
        if p.exists(): return pd.read_csv(p)
    raise FileNotFoundError(f"Missing {n}; expected in data/ or repository root.")

sec,pr,pos,ca,tr,cp,src,rules=[load(n) for n in ["securities.csv","prices.csv","positions.csv","corporate_actions.csv","transactions.csv","counterparties.csv","sources.csv","quality_rules.csv"]]
pages=["Executive overview","Security & issuer master","Reference data","Pricing hierarchies","Data integration","Data quality & exceptions","Positions & corporate actions","Transactions & counterparties","Analytics & history","Dynamic Document Studio","Data distribution & lineage","Product configuration"]
page=st.sidebar.radio("Workspace",pages)
st.sidebar.caption("Synthetic data snapshot · 21 Nov 2026")

def metrics(vals):
    cols=st.columns(len(vals))
    for c,(a,b) in zip(cols,vals): c.metric(a,b)
def dl(df,name):
    st.download_button("Download CSV",df.to_csv(index=False).encode(),name,"text/csv")

if page=="Executive overview":
    st.subheader("Enterprise data operations")
    metrics([("Securities",len(sec)),("Price observations",len(pr)),("Positions",len(pos)),("Corporate actions",len(ca)),("Data sources",len(src))])
    a,b=st.columns(2)
    with a:
        st.markdown("**Securities by asset class**"); st.bar_chart(sec.groupby("asset_class").size())
        st.markdown("**Price observations by vendor**"); st.bar_chart(pr.groupby("vendor").size())
    with b:
        st.markdown("**Portfolio market value**"); st.bar_chart(pos.groupby("portfolio").market_value.sum())
        st.markdown("**Corporate actions by type**"); st.bar_chart(ca.groupby("event_type").size())
    st.markdown("**Operational data-quality indicators**")
    st.dataframe(pd.DataFrame([["Identifier completeness","98.2%","Illustrative"],["Fresh price observations","92.5%","Illustrative"],["Position reconciliation","99.1%","Illustrative"],["Lineage coverage","96.0%","Illustrative"]],columns=["Metric","Value","Basis"]),use_container_width=True,hide_index=True)

elif page=="Security & issuer master":
    st.subheader("Security and issuer master")
    q=st.text_input("Search security, ticker, identifier, issuer or universe")
    ac=st.multiselect("Asset class",sorted(sec.asset_class.unique()),default=sorted(sec.asset_class.unique()))
    v=sec[sec.asset_class.isin(ac)]
    if q: v=v[v.astype(str).apply(lambda c:c.str.contains(q,case=False,na=False)).any(axis=1)]
    st.dataframe(v,use_container_width=True,hide_index=True); dl(v,"security_master.csv")
    issuer=st.selectbox("Issuer relationship",sorted(sec.issuer.unique()))
    st.dataframe(sec[sec.issuer==issuer],use_container_width=True,hide_index=True)

elif page=="Reference data":
    st.subheader("Master reference datasets")
    t=st.tabs(["Securities","Prices","Positions","Corporate actions"])
    for tab,df in zip(t,[sec,pr,pos,ca]):
        with tab: st.dataframe(df,use_container_width=True,hide_index=True)

elif page=="Pricing hierarchies":
    st.subheader("Firm- and portfolio-level pricing hierarchies")
    portfolio=st.selectbox("Policy scope",["Firm default"]+sorted(pos.portfolio.unique()))
    ticker=st.selectbox("Security",sec.ticker.tolist())
    age=st.slider("Maximum price age (hours)",1,168,24)
    overrides={"Growth Fund":["Vendor Beta","Vendor Alpha","Vendor Gamma"],"Income Fund":["Vendor Gamma","Vendor Alpha","Vendor Beta"],"Global Macro Fund":["Vendor Alpha","Vendor Gamma","Vendor Beta"]}
    order=overrides.get(portfolio,["Vendor Alpha","Vendor Beta","Vendor Gamma"])
    st.write("Source priority: "+" → ".join(order))
    p=pr[pr.ticker==ticker].copy(); p["as_of_dt"]=pd.to_datetime(p.as_of)
    p["age_hours"]=(pd.Timestamp("2026-11-21 12:00")-p.as_of_dt).dt.total_seconds()/3600
    p["fresh"]=p.age_hours<=age; p["priority"]=p.vendor.map({v:i+1 for i,v in enumerate(order)}).fillna(99); p["eligible"]=p.fresh&p.price.notna()
    st.dataframe(p[["vendor","price","currency","as_of","age_hours","fresh","priority","eligible"]].sort_values("priority"),use_container_width=True,hide_index=True)
    e=p[p.eligible].sort_values(["priority","as_of_dt"],ascending=[True,False])
    if len(e):
        x=e.iloc[0]; st.success(f"Selected demo price: {x.price} {x.currency} from {x.vendor}.")
    else: st.warning("No eligible price. Route to pricing exception review; do not silently use stale data.")
    st.caption("Illustrative hierarchy only; actual valuation policies require governance and approval.")

elif page=="Data integration":
    st.subheader("Integrated systems and source registry")
    st.dataframe(src,use_container_width=True,hide_index=True)
    f=st.file_uploader("Upload a CSV to inspect incoming schema",type=["csv"])
    if f:
        x=pd.read_csv(f); st.success(f"Schema preview: {len(x)} rows, {len(x.columns)} columns")
        st.write(list(x.columns)); st.dataframe(x.head(20),use_container_width=True)
        st.caption("Upload is not persisted or distributed.")
    a,b=st.columns(2)
    with a:
        st.markdown("**API integration concept**")
        st.code("POST /demo/v1/reference-data\nGET /demo/v1/securities/{security_id}\nGET /demo/v1/prices?ticker=AAPL")
        st.caption("Endpoint examples only; no API server is running.")
    with b:
        st.markdown("**Snowflake Data Share concept**")
        st.code("DATABASE: INVESTMENT_DATA_SHARE\nSCHEMA: REFERENCE\nVIEWS: SECURITY_MASTER, PRICES, POSITIONS")
        st.caption("No live Snowflake account or share is connected.")
    st.write("Adaptor concepts: market data vendor · custodian · OMS · PMS · accounting platform · fund administrator.")

elif page=="Data quality & exceptions":
    st.subheader("Automated data-quality controls")
    checks=[
    ("DQ-01 Required security ID","Security master",sec.security_id.isna().sum(),"Critical","Internal key required"),
    ("DQ-02 Duplicate security ID","Security master",sec.security_id.duplicated().sum(),"High","Keys must be unique"),
    ("DQ-03 Applicable ISIN present","Security master",sec.loc[sec.asset_class.isin(["Equity","ETF","Fixed Income"]),"isin"].isna().sum(),"Medium","Applicable instruments should have ISIN"),
    ("DQ-04 Non-positive price","Prices",(pr.price<=0).sum(),"Critical","Price must be positive"),
    ("DQ-05 Missing price timestamp","Prices",pr.as_of.isna().sum(),"High","Timestamp required"),
    ("DQ-06 Negative position quantity","Positions",(pos.quantity<0).sum(),"High","Shorts require explicit treatment"),
    ("DQ-07 Missing trade ID","Transactions",tr.trade_id.isna().sum(),"Critical","Trade ID required"),
    ("DQ-08 Duplicate counterparty ID","Counterparties",cp.counterparty_id.duplicated().sum(),"High","Keys must be unique")]
    res=pd.DataFrame(checks,columns=["rule","dataset","failures","severity","control"]); res["result"]=res.failures.map(lambda x:"PASS" if x==0 else "FAIL")
    metrics([("Rules executed",len(res)),("Passed",int((res.result=="PASS").sum())),("Failed",int((res.result=="FAIL").sum()))])
    st.dataframe(res,use_container_width=True,hide_index=True); dl(res,"data_quality_results.csv")
    st.markdown("**Exception review queue**")
    q=pd.DataFrame([["DQX-101","Stale price","High","Pricing Operations","Check timestamp and approved fallback"],["DQX-102","Identifier conflict","Critical","Reference Data","Validate issuer mapping"],["DQX-103","Position break","High","Investment Operations","Compare internal and custodian holdings"],["DQX-104","Corporate action mismatch","Medium","Asset Servicing","Confirm event terms and dates"]],columns=["id","issue","severity","owner","next_action"])
    st.dataframe(q,use_container_width=True,hide_index=True)

elif page=="Positions & corporate actions":
    st.subheader("Positions and asset servicing")
    a,b=st.tabs(["Positions","Corporate actions"])
    with a:
        pf=st.selectbox("Portfolio",sorted(pos.portfolio.unique())); x=pos[pos.portfolio==pf]
        metrics([("Records",len(x)),("Market value",f"${x.market_value.sum():,.2f}"),("Securities",x.security_id.nunique())])
        st.dataframe(x,use_container_width=True,hide_index=True)
    with b:
        s=st.multiselect("Event status",sorted(ca.status.unique()),default=sorted(ca.status.unique()))
        st.dataframe(ca[ca.status.isin(s)],use_container_width=True,hide_index=True)

elif page=="Transactions & counterparties":
    a,b=st.tabs(["Transactions","Counterparties"])
    with a:
        s=st.multiselect("Trade status",sorted(tr.status.unique()),default=sorted(tr.status.unique()))
        st.dataframe(tr[tr.status.isin(s)],use_container_width=True,hide_index=True); dl(tr[tr.status.isin(s)],"transactions.csv")
    with b: st.dataframe(cp,use_container_width=True,hide_index=True)

elif page=="Analytics & history":
    st.subheader("Live-style and historical analytics")
    ticker=st.selectbox("Ticker",sec.ticker.tolist(),key="history")
    x=pr[pr.ticker==ticker].copy(); x["as_of"]=pd.to_datetime(x.as_of)
    st.line_chart(x.sort_values("as_of").set_index("as_of").price)
    st.dataframe(x,use_container_width=True,hide_index=True)
    st.bar_chart(pos.groupby("portfolio").market_value.sum())

elif page=="Dynamic Document Studio":
    st.subheader("Reusable document generation")
    template=st.selectbox("Template",["Daily Data Quality Report","Portfolio Reference Data Report","Pricing Source Review","Corporate Actions Register"])
    title=st.text_input("Report title",template); audience=st.selectbox("Audience",["Investment Operations","Data Governance","Portfolio Management","Risk & Compliance"])
    include=st.checkbox("Include detailed data table",True)
    if st.button("Generate report",type="primary"):
        if template=="Daily Data Quality Report": df=rules; summary="Data quality control catalogue and exception review considerations."
        elif template=="Portfolio Reference Data Report": df=sec; summary="Mastered security and issuer reference dataset."
        elif template=="Pricing Source Review": df=pr; summary="Vendor price observations and pricing-source review."
        else: df=ca; summary="Corporate action event register and key dates."
        md=f"# {title}\n\n**Audience:** {audience}\n\n**Generated:** {datetime.now():%Y-%m-%d %H:%M}\n\n{summary}\n"
        if include: md+="\n## Detail\n\n"+df.to_markdown(index=False)
        st.success("Report generated.")
        st.download_button("Download report (Markdown)",md.encode(),"financial_data_report.md","text/markdown")
        dl(df,"report_detail.csv")

elif page=="Data distribution & lineage":
    st.subheader("Single-source data distribution")
    st.code("Source systems → ingestion → validation → mastered data → controlled distribution → downstream consumers")
    lin=pd.DataFrame([["Market data vendor","Price feed","Schema + freshness checks","Pricing service","Portfolio platform"],["Custodian","Position file","Identifier + quantity checks","Position master","Accounting"],["Corporate actions provider","Event notice","Event + date validation","Asset servicing","Portfolio operations"],["OMS","Trade event","Required fields + counterparty checks","Transaction master","Downstream books"]],columns=["source","input","controls","mastered service","destination"])
    st.dataframe(lin,use_container_width=True,hide_index=True)
    choice=st.selectbox("Export dataset",["Securities","Prices","Positions","Corporate actions","Transactions"])
    df={"Securities":sec,"Prices":pr,"Positions":pos,"Corporate actions":ca,"Transactions":tr}[choice]
    dl(df,"controlled_data_export.csv")

else:
    st.subheader("Product configuration and governance")
    st.markdown("**Configurable modules**")
    st.write("Security master · pricing · positions · corporate actions · transactions · data quality · analytics · reporting · distribution.")
    st.markdown("**Governance principles**")
    st.write("Canonical identifiers; issuer relationships; source precedence; validation before distribution; exception ownership; lineage and audit; controlled access.")
    st.dataframe(pd.DataFrame([["Scalability","Partitioning, batch processing and horizontal scaling","Not load-tested"],["Availability","Monitoring, retries and recovery","Conceptual"],["Security","RBAC, encryption, secrets and audit","Not implemented"],["Interoperability","Versioned APIs, schema contracts and adaptors","Simulated"],["Data history","Effective dating and retention","Conceptual"]],columns=["Area","Production consideration","Prototype status"]),use_container_width=True,hide_index=True)
    st.warning("This prototype does not implement live feeds, actual APIs, Snowflake connectivity, production MDM, official valuation, persistent approvals, or enterprise-scale throughput.")

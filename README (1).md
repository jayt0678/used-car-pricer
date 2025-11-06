
# Used Car Fast-Sale Pricer (Streamlit)

A tiny app to build a **competitive set** and a **fast-sale price** for any used vehicle. Upload your listings CSV (active + sold), paste a VIN to auto-fill basics, and click **Run Pricing**.

## Local Setup

```bash
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
streamlit run streamlit_app.py
```

- Edit `requirements.txt` as needed. Defaults:
  ```
  streamlit==1.39.0
  pandas==2.2.2
  numpy==1.26.4
  requests==2.32.3
  ```

## CSV Schema (required headers)

`listing_id,status,year,make,model,trim,body,drivetrain,transmission,mileage,options_score,accident,cpo,seller_dealer,lat,lon,price,list_date,sold_date,dom,distance_km`

> If `distance_km` is blank, the app computes it from lat/lon.

## VIN Decoding

The app uses the **NHTSA vPIC** endpoint:
`https://vpic.nhtsa.dot.gov/api/vehicles/DecodeVinValuesExtended/{VIN}?format=json`

- If VIN decode fails (offline, rate limit, unusual VIN), just fill fields manually.
- Decoded fields include Year, Make, Model, Trim, Body class, Drive type, and Transmission.

## Deploy to Streamlit Community Cloud

1. Push these files to a **public GitHub repo**:
   - `streamlit_app.py`
   - `comp_pricer.py`
   - `requirements.txt`
   - `sample_listings.csv` (optional)
   - `README.md`

2. Go to https://streamlit.io/cloud → **Deploy an app** → choose your repo/branch, main file `streamlit_app.py`.

3. No secrets needed. If you want to use a private VIN service, add your key in **Secrets** and update the code accordingly.

## Tips

- Include **sold + active** listings from the last **30–60 days**.
- Add **lat/lon** for both target and listings to compute distance (better comp selection).
- Adjust **α (mileage elasticity)** if your market penalizes mileage more/less.
- For ultra-fast sale, list near the **10th percentile** of the weighted distribution.

Enjoy! 🚗

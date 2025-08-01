from flask import Flask, request, render_template
import numpy as np
import pickle
import sklearn
import pandas as pd

print(sklearn.__version__)

# Load models
dtr = pickle.load(open('dtr.pkl', 'rb'))
preprocessor = pickle.load(open('processor.pkl', 'rb'))

# Load dataset to extract valid Area and Item values
df = pd.read_csv('./archive/yield_df.csv')  # Replace with actual dataset filename
valid_areas = sorted(df['Area'].dropna().unique().tolist())
valid_items = sorted(df['Item'].dropna().unique().tolist())

# Flask app
app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html', areas=valid_areas, items=valid_items)

@app.route("/predict", methods=['POST'])
def predict():
    if request.method == 'POST':
        try:
            Year = int(request.form['Year'])
            average_rain_fall_mm_per_year = float(request.form['average_rain_fall_mm_per_year'])
            pesticides_tonnes = float(request.form['pesticides_tonnes'])
            avg_temp = float(request.form['avg_temp'])
            Area = request.form['Area']
            Item = request.form['Item']

            # Prepare features
            features = pd.DataFrame([{
                'Area': Area,
                'Item': Item,
                'Year': Year,
                'average_rain_fall_mm_per_year': average_rain_fall_mm_per_year,
                'pesticides_tonnes': pesticides_tonnes,
                'avg_temp': avg_temp
            }])

            transformed_features = preprocessor.transform(features)
            prediction = dtr.predict(transformed_features)[0]

            # Extract past data for chart
            historical = df[(df['Area'] == Area) & (df['Item'] == Item)].sort_values(by='Year')
            years = historical['Year'].tolist()
            yields = historical['hg/ha_yield'].tolist()  # Adjust this column name to match yours

            return render_template('index.html',
                                   prediction=round(prediction, 2),
                                   areas=valid_areas,
                                   items=valid_items,
                                   years=years,
                                   yields=yields,
                                   selected_area=Area,
                                   selected_item=Item)
        except Exception as e:
            return render_template('index.html', prediction=f"Error: {e}",
                                   areas=valid_areas, items=valid_items)

if __name__ == "__main__":
    app.run(debug=True)

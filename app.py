from flask import Flask, render_template, request, redirect
from pandas import *
import requests
import pandas as pd
import json
from bokeh.io import output_notebook, output_file, show
from bokeh.plotting import figure, curdoc
from bokeh.models import ColumnDataSource
from bokeh.models import DatetimeTickFormatter
from bokeh.embed import components
from bokeh.resources import INLINE

app = Flask(__name__, template_folder='templates')

app.choices=[]

@app.route('/', methods = ['GET','POST'])
def index():
    return render_template('index.html')

@app.route('/about', methods = ['GET','POST'])
def about():
    
    if request.method == 'POST':
        app.choices = request.form.getlist('Stock_Ticker')
    
    filepath = 'https://www.quandl.com/api/v3/datasets/WIKI/'+app.choices[0]+'.csv'
    data = read_csv(filepath, index_col = 'Date', parse_dates = True )
    new_data = data.iloc[::-1]
    new_index = pd.date_range(start=new_data.index[0],end = new_data.index[-1], freq = 'D')
    new_data = new_data.reindex(new_index)
    subset_index = pd.date_range(start='2017-01-01',end = '2017-01-31',freq ='D')
    subset = new_data.loc[subset_index]
    data_source = ColumnDataSource(subset.dropna())
    cols = []
    i = 0
    while i < (len(app.choices)-1):
        if app.choices[i+1] == '1':
            cols.append('High')
        elif app.choices[i+1] == '2':
            cols.append('Adj. High')
        elif app.choices[i+1] == '3':
            cols.append('Low')
        elif app.choices[i+1] == '4':
            cols.append('Adj. Low')
        i = i+1
    
    p = figure(x_axis_type = 'datetime', title="Quandl WIKI Stock Prices - Jan 2017")
    p.xaxis.formatter = DatetimeTickFormatter(days = '%d')
    p.xgrid.grid_line_color = None
    p.ygrid.grid_line_color = None
    p.xaxis.axis_label = 'date'
    
    i = 0
    while i < len(cols):
        if cols[i] == 'High':
            p.line(x = subset.dropna().index, y = data_source.data[cols[i]] , line_color = 'red', legend_label = cols[i])
        elif cols[i] == 'Adj. High':
            p.line(x = subset.dropna().index, y = data_source.data[cols[i]] , line_color = 'green', legend_label = cols[i])
        elif cols[i] == 'Low':
            p.line(x = subset.dropna().index, y = data_source.data[cols[i]] , line_color = 'blue', legend_label = cols[i])
        elif cols[i] == 'Adj. Low':
            p.line(x = subset.dropna().index, y = data_source.data[cols[i]] , line_color = 'yellow', legend_label = cols[i])    
        i = i + 1
    
    p.legend.location = "top_left"
    p.legend.click_policy="hide"
    
    script, div = components(p, INLINE)
    js_resources = INLINE.render_js()
    css_resources = INLINE.render_css()
    title = 'Graph of ' + app.choices[0] + ' data'
    
    return render_template('about.html', plot_script=script, plot_div=div,
                          js_resources = js_resources,
                          css_resources = css_resources, webpage_title = title )

if __name__ == '__main__':
    #app.run()
    app.run(debug=True, port=33507)

"""Bokeh Dashboard"""

from flask import Flask, render_template
from datetime import date

from bokeh.models.widgets import Tabs, Panel
from bokeh.plotting import output_file, curdoc
from bokeh.layouts import column, layout, row, Spacer
from bokeh.embed import components
from bokeh.resources import INLINE
from bokeh.sampledata.autompg import autompg_clean as df

from utils import (clean_main_data,
                    create_cds, create_filtered_cds,
                    create_fig, create_second_fig,
                    create_callback, create_logo, create_title, create_display)

app = Flask(__name__)

@app.route('/')

def index():
    # df_main, df_pv = load_data(sys.argv[1])
    df_main = df
    df_main = clean_main_data(df_main)
    cds_main = create_cds(df_main)

    group_filter, filtered_main = create_filtered_cds(cds_main, 'category')

    figs, legends, all_sizes = create_fig('x_active','y_active', 'category', 
                                            filtered_main, 'sizes', cds_main)
    figs, x_selection, y_selection, categ_selection, resize_selection, subcateg_selection, units_selection = create_callback(figs, legends, all_sizes, cds_main, group_filter, filtered_main)

    # Add display with the hovertool contents
    display1 = create_display(figs[0], cds_main)
    display2 = create_display(figs[1], cds_main)

    m_fig_linear = create_second_fig('kpl','hp',cds_main,'linear')
    m_fig_log = create_second_fig('kpl','hp',cds_main,'log')

    w_fig_linear = create_second_fig('weight','accel', cds_main, 'linear')
    w_fig_log = create_second_fig('weight','accel', cds_main, 'log')

    tab1_layout = row(figs[0], column(m_fig_linear, w_fig_linear, Spacer(height=50), display1))
    tab2_layout = row(figs[1], column(m_fig_log, w_fig_log, Spacer(height=50), display2))

    # Create Tabs
    tab_linear = Panel(child=tab1_layout, title='Linear')
    tab_log = Panel(child=tab2_layout, title='Log')

    # Add image
    image = create_logo()
    title = create_title()

    # Put the Panels in a Tabs object
    tabs = Tabs(tabs=[tab_log, tab_linear], height=100)
    layout = column(Spacer(width=50),
                row(image, title),
                row(column(Spacer(height=120),
                units_selection,
                Spacer(height=45),
                x_selection,
                Spacer(height=15),
                y_selection,
                Spacer(height=15),
                categ_selection,
                Spacer(height=15),
                resize_selection,
                Spacer(height=15),
                subcateg_selection),
        Spacer(width=50),
        tabs))

    script, div = components(layout)
    
    # Get today's date to save tool with updated version
    # today = date.today()
    # d1 = today.strftime("%d_%m_%Y")

    # Uncomment this section to export the dashboard as a standalone application in html file
    # Run the code in cml as "py main.py"
    '''out = output_file('example_{}.html'.format(d1))

    bokeh.io.save(
        layout,
        filename=out,
        title='Example Autompg Bokeh')'''

    # Uncomment this section to launch the application using the bokeh server
    # Run the code in cml as "bokeh serve --show main.py"
    # curdoc().add_root(layout)
    # curdoc().title = "Example Autompg Bokeh"

    return render_template(
        'index.html',
        plot_script=script,
        plot_div=div,
        js_resources=INLINE.render_js(),
        css_resources=INLINE.render_css()
        ).encode(encoding='UTF-8')

if __name__ == "__main__":
    app.run(debug=True)

import pandas as pd
import numpy as np

from bokeh import events
from bokeh.models import (CDSView, GroupFilter, ColumnDataSource, Select, CustomJS,
                            Legend, LinearInterpolator, MultiChoice, RadioButtonGroup)
from bokeh.models.tools import HoverTool
from bokeh.plotting import figure
from bokeh.palettes import (Category20_20, Category20b_20, Accent8, Spectral11, Category10_10,
                            Dark2_8, Bokeh8, Colorblind8, Pastel1_9, Set3_12)
from bokeh.models.widgets import Div

from js_codes import (js_code_x, js_code_y, js_code_cat, js_code_subcat, js_code_res,
                    display_code, units_code)
from lists import (xy_options, xy_options_imper, resizeby_options, resizeby_options_imper,
                    floats_metric, ints_metric, colorby_options, categories)
from html_codes import tooltip, dashboard_title

def convert_units(df):
    """Create new columns with converted values from the input database (metric to imperial)."""
    df['weight_lbs'] = df['weight_kg']*2.205
    df['kpl'] = df['mpg']/2.352
    return df

def clean_main_data(df_main):
    """Clean imported database"""
    df_main['weight_kg'] = df_main['weight']
    # Fill N/A values with zeros
    df_main = df_main.fillna(0)
    # Convert categorical and numerical data to string, floats, ints
    df_main[categories] = df_main[categories].astype(str)
    df_main[floats_metric] = df_main[floats_metric].astype(float)
    df_main[floats_metric] = df_main[floats_metric].round(decimals=3)
    df_main[ints_metric] = df_main[ints_metric].astype(int)
    # Sort dataset by 'Customer'
    df_main = df_main.sort_values(by=['name'])
    
    # Create columns in imperial system
    df_main = convert_units(df_main)

    # Create new columns that will be updated in the callbacks
    df_main['Nonecol'] = 'None'
    df_main['None'] = 5
    df_main['Img'] = 'https://thumbs.dreamstime.com/b/example-red-tag-example-red-square-price-tag-117502755.jpg'
    df_main['x_active'] = df_main['kpl']
    df_main['y_active'] = df_main['hp']
    df_main['category'] = df_main['mfr']
    df_main['sizes'] = df_main['None']
    return df_main

def create_cds(df):
    """Create bokeh's column data source from database."""
    source = ColumnDataSource(data=df)
    return source

def create_filtered_cds(source_main, category):
    """Generate different views (colors) based on each category."""
    filtered_views = []
    group_filter = []
    for cat in np.unique(list(source_main.data[category])):
        gr_filter = GroupFilter(column_name=category, group=cat)
        filtered_view = CDSView(source=source_main, filters=[gr_filter])
        filtered_views.append(filtered_view)
        group_filter.append(gr_filter)
    return group_filter, filtered_views

def hover_specs():
    """Create hovertool that will display the tooltip contents."""
    hover = HoverTool(tooltips=tooltip)
    return hover

def create_fig(x, y, category, filtered_views, sizes, source):
    """Create interactive main graph."""
    # Create list of colors to categorize data
    my_colors = list(Category20_20 + Category20b_20 + Accent8 + Spectral11 + 
                        Category10_10 + Dark2_8 + Bokeh8 + Colorblind8 + Pastel1_9 + 
                        Set3_12)
    # Load hovertool
    hover = hover_specs()
    tools = [hover,'tap','pan','wheel_zoom','box_zoom','reset','save']
    # Create figure
    legends = []
    figs = []
    all_sizes = []
    for scales in ['linear', 'log']:
        fig = figure(plot_width = 900, plot_height = 880, x_axis_type=scales, y_axis_type=scales, tools=tools)
        legend_it = []
        cirs_sizes = []
        # Plot individually legend items and glyphs
        for cat, view, one_color in zip(np.unique(list(source.data[category])), filtered_views, my_colors):
            cir = fig.circle(x, y, fill_alpha=0.7, source=source,
                            view=view,
                            color=one_color)
            legend_it.append((cat, [cir]))
            cir.glyph.size = {'field':'sizes',
                        'transform': LinearInterpolator(x=[source.data[sizes].min(), source.data[sizes].max()],
                                                        y=[15,70])}
            cirs_sizes.append(cir.glyph.size)
        legend = Legend(items=legend_it, location=(10, 400))
        legend.click_policy='mute'
        legend.label_text_font_size = '8pt'
        legend.spacing = -8
        fig.add_layout(legend, 'right')
        figs.append(fig)
        legends.append(legend)
        all_sizes.append(cirs_sizes)
    return figs, legends, all_sizes

def create_second_fig(x,y, source, scales):
    """Create supporting graph - static, not interactive"""
    fig = figure(plot_width = 400, plot_height = 250, x_axis_type=scales, y_axis_type=scales)
    fig.scatter(x, y, fill_alpha=0.8, size=10,
                source=source, color=Category20_20[0],
                selection_color='firebrick')
    fig.xaxis.axis_label = x
    fig.yaxis.axis_label = y
    fig.title.text = f'{x} vs {y}'
    return fig

def create_callback(figs, legends, all_sizes, source, group_filter, filtered_views):
    """Create callbacks used to update values in the dashboard."""
    units_selection = RadioButtonGroup(labels=["Metric","Imperial"],
                        active=0,
                        width_policy="fit")
    x_selection = Select(title="X Value",
                        options=xy_options,
                        value="mpg",
                        width_policy="fit")
    y_selection = Select(title="Y Value",
                        options=xy_options,
                        value="hp",
                        width_policy="fit")
    categ_selection = Select(title="Color By",
                        options=colorby_options+["None"],
                        value="mfr",
                        width_policy="fit")
    sub = list(np.unique(list(source.data[categ_selection.value])).tolist())
    subcateg_selection = MultiChoice(
                        title='Filter By',
                        options=sub,
                        width_policy="fit")
    resize_selection = Select(title="Resize By",
                        options=resizeby_options+["None"],
                        value="None",
                        width_policy="fit")
    units_update = CustomJS(args=dict(source=source,
                                        units_selection=units_selection,
                                        xy_options_metric=xy_options,
                                        xy_options_imper=xy_options_imper,
                                        resizeby_options_metric=resizeby_options+["None"],
                                        resizeby_options_imper=resizeby_options_imper+["None"],
                                        x_selection=x_selection,
                                        y_selection=y_selection,
                                        resize_selection=resize_selection),
                            code=units_code)
    x_update_curve = CustomJS(args=dict(source=source,
                                        fig0 = figs[0],
                                        fig1 = figs[1],
                                        xaxis1=figs[0].xaxis,
                                        xaxis2=figs[1].xaxis,
                                        title1=figs[0].title,
                                        title2=figs[1].title,
                                        x_selection=x_selection,
                                        y_selection=y_selection),
                            code=js_code_x)
    y_update_curve = CustomJS(args=dict(source=source,
                                        fig0 = figs[0],
                                        fig1 = figs[1],
                                        yaxis1=figs[0].yaxis,
                                        yaxis2=figs[1].yaxis,
                                        title1=figs[0].title,
                                        title2=figs[1].title,
                                        x_selection=x_selection,
                                        y_selection=y_selection),
                            code=js_code_y)
    cat_update_curve = CustomJS(args=dict(source=source,
                                        categ_selection=categ_selection,
                                        subcateg_selection=subcateg_selection,
                                        filtered_views=filtered_views,
                                        group_filter=group_filter,
                                        legend1=legends[0],
                                        legend2=legends[1]),
                            code=js_code_cat)
    subcat_update_curve = CustomJS(args=dict(source=source,
                                        categ_selection=categ_selection,
                                        subcateg_selection=subcateg_selection,
                                        legend1=legends[0],
                                        legend2=legends[1]),
                            code=js_code_subcat)
    res_update_curve = CustomJS(args=dict(source=source,
                                        sizes0 = all_sizes[0],
                                        sizes1 = all_sizes[1],
                                        resize_selection=resize_selection),
                            code=js_code_res)

    units_selection.js_on_click(units_update)
    x_selection.js_on_change('value', x_update_curve)
    y_selection.js_on_change('value', y_update_curve)
    categ_selection.js_on_change('value', cat_update_curve)
    subcateg_selection.js_on_change('value', subcat_update_curve)
    resize_selection.js_on_change('value', res_update_curve)

    figs[0].xaxis.axis_label = x_selection.value
    figs[0].yaxis.axis_label = y_selection.value
    figs[0].legend.title = categ_selection.value
    figs[0].title.text = f'{y_selection.value} vs {x_selection.value}'
    figs[0].title.text_font_size = "15px"

    figs[1].xaxis.axis_label = x_selection.value
    figs[1].yaxis.axis_label = y_selection.value
    figs[1].legend.title = categ_selection.value
    figs[1].title.text = f'{y_selection.value} vs {x_selection.value}'
    figs[1].title.text_font_size = "15px"
    return figs, x_selection, y_selection, categ_selection, resize_selection, subcateg_selection, units_selection

def create_logo():
    """Load figure that will be displayed in the main page."""
    source="https://as1.ftcdn.net/v2/jpg/01/82/99/00/1000_F_182990099_35RBIu4gFEDNOoIp7dntrwHIjltzx4sq.jpg"
    div_image = Div(text=f"""<img src={source} width=310 alt="div_image">""", width=350, height=70)
    return div_image

def create_title():
    """Create the title of the dashboard."""
    div_title = Div(text=dashboard_title, width=1310, height=70)
    return div_title

def create_display(plot, source):
    """Create side window that will display the same information as the hovertool."""
    text_box = Div(width=400, height=100, height_policy="fixed")
    attributes = ['name', 'mfr', 'origin', 'yr', 'accel',
                    'hp', 'displ']
    style = 'float:left;clear:left;font_size=13px'
    display_event = CustomJS(args=dict(div=text_box, source=source),
                            code=display_code % (attributes, style))
    plot.js_on_event(events.Tap, display_event)
    return text_box
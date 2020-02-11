from bokeh.plotting import figure, ColumnDataSource
from bokeh.layouts import row, column, widgetbox
from bokeh.models import HoverTool, Slider, CustomJS
from bokeh.embed import json_item
from . import data

def create_hbar(area, plot_data, y_variables=data.model_vars, y_definition=data.label_def_ordered, 
y_extra_info=data.label_extra_ordered, div_name="myplot"):
	values = plot_data.to_numpy()
	values = values[0]

	all_data = ColumnDataSource(data=dict({'variables': y_variables,
				'values': values,
				'definition': y_definition,
				'variables_extra': y_extra_info}))

	tooltips = """
	<div style="width:200px;">
			<div>
                <span style="font-size: 15px; color:blue">Variable:</span>
                <span style="font-size: 12px;">@variables_extra</span>
            </div>
            <div>
                <span style="font-size: 15px; color:blue">Percentage:</span>
                <span style="font-size: 12px;">@values{1.1} %</span>
            </div>
            <div>
                <span style="font-size: 15px; color:blue">Explanation:</span>
                <span style="font-size: 12px;">@definition</span>
            </div>
        </div>
	"""

	TOOLS = "hover,box_zoom,reset"
	plot = figure(plot_height = 600, plot_width = 800, 
	          x_axis_label = 'Percentage', 
	           #y_axis_label = ,
	           x_range=(0,100), y_range=y_variables, tools=TOOLS, tooltips=tooltips)

	plot.square(x='values', y='variables', fill_color='blue', line_alpha = 0.75, size='values', angle='values',
	        hover_fill_color = 'red', source=all_data)
	plot.title.text = "Just some random sliders and their values represented in the graph"
	
	part_rent_slider = Slider(start=0, end=100, value=10, step=1, title="Private rental")
	corp_rent_slider = Slider(start=0, end=100, value=20, step=1, title="Housing corporation rental")
	high_rent_slider = Slider(start=0, end=100, value=30, step=1, title="High rent (> 971 euro)")
	middle_rent_slider = Slider(start=0, end=100, value=40, step=1, title="Middle high rent (711 - 971 euro)")
	low_rent_slider = Slider(start=0, end=100, value=50, step=1, title="Low rent (< 711 euro)")
	living_space_040 = Slider(start=0, end=100, value=60, step=1, title="Living space of 0-40 m2")
	living_space_4060 = Slider(start=0, end=100, value=70, step=1, title="Living space of 40-60 m2")
	living_space_6080 = Slider(start=0, end=100, value=80, step=1, title="Living space of 60-80 m2")
	living_space_80100 = Slider(start=0, end=100, value=90, step=1, title="Living space of 80-100 m2")
	living_space_100 = Slider(start=0, end=100, value=100, step=1, title="Living space of > 100 m2")

	all_sliders = [part_rent_slider, corp_rent_slider, high_rent_slider,middle_rent_slider, low_rent_slider, 
	living_space_100, living_space_80100, living_space_6080, living_space_4060, living_space_040]

	callback = CustomJS(args=dict(source=all_data), code="""
		var data = source.data;
		var values = data["values"];

		var value = cb_obj.value;
		var var_text = cb_obj.title;

        var variable;
		var value_idx;
		updatePlot(value, var_text);
        socket.on('plot_update', function(msg) {
            value = msg.new_value;
            variable = msg.variable;
			value_idx = msg.index;

			values[value_idx] = value;
			data.values = values;
			source.data = data;
			source.change.emit();

			window.onmouseup = function() {
				updateModel(value, variable);
			}
        });
	""")

	for slider in all_sliders:
		slider.js_on_change('value', callback)

	layout = row(
	    plot,
	    column(*all_sliders),
		width=800
	)

	plot_json = json_item(layout, div_name)

	return plot_json
import plotly.plotly as py
from plotly.graph_objs import Figure,XAxis,YAxis
from plotlytools import getLayout
import auth


def strip_figures(figure):
	"""
	Strips a figure into multiple figures with a trace on each of them

	Parameters:
	-----------
		figure : Figure
			Plotly Figure
	"""
	fig=[]
	for trace in figure['data']:
		fig.append(Figure(data=[trace],layout=figure['layout']))
	return fig


def get_base_layout(figs):
	"""
	Generates a layout with the union of all properties of multiple
	figures' layouts

	Parameters:
	-----------
		fig : list(Figures)
			List of Plotly Figures
	"""
	layout={}
	for fig in figs:
		for k,v in fig['layout'].items():
			layout[k]=v
	return layout

def figures(df,specs):
	"""
	Generates multiple Plotly figures for a given DataFrame

	Parameters:
	-----------
		df : DataFrame
			Pandas DataFrame
		specs : list(dict)
			List of dictionaries with the properties 
			of each figure. 
			All properties avaialbe can be seen with
			help(cufflinks.pd.DataFrame.iplot)
	"""
	figs=[]
	for spec in specs:
		figs.append(df.figure(**spec))
	return figs

def subplots(figures,shape=None,
				  shared_xaxes=False, shared_yaxes=False,
				  start_cell='top-left', theme='pearl',base_layout=None,
				  **kwargs):
	"""
	Generates a subplot view for a set of figures
	This is a wrapper for plotly.tools.make_subplots

	Parameters:
	-----------
		figures : [Figures]
			List of Plotly Figures
		shape : (rows,cols)
			Tuple indicating the size of rows and columns
			If omitted then the layout is automatically set
		shared_xaxes : bool
			Assign shared x axes.
			If True, subplots in the same grid column have one common
			shared x-axis at the bottom of the gird.
		shared_yaxes : bool
			Assign shared y axes.
			If True, subplots in the same grid row have one common
			shared y-axis on the left-hand side of the gird.
		start_cell : string
				'bottom-left'
				'top-left'
			Choose the starting cell in the subplot grid used to set the
			domains of the subplots.
		theme : string
			Layout Theme
				solar
				pearl
				white		
			see cufflinks.getThemes() for all 
			available themes
		horizontal_spacing : float
				[0,1]
			Space between subplot columns.
		vertical_spacing : float
			Space between subplot rows.
		specs : list of dicts
			Subplot specifications.
				ex1: specs=[[{}, {}], [{'colspan': 2}, None]]
				ex2: specs=[[{'rowspan': 2}, {}], [None, {}]]

			- Indices of the outer list correspond to subplot grid rows
			  starting from the bottom. The number of rows in 'specs'
			  must be equal to 'rows'.

			- Indices of the inner lists correspond to subplot grid columns
			  starting from the left. The number of columns in 'specs'
			  must be equal to 'cols'.

			- Each item in the 'specs' list corresponds to one subplot
			  in a subplot grid. (N.B. The subplot grid has exactly 'rows'
			  times 'cols' cells.)

			- Use None for blank a subplot cell (or to move pass a col/row span).

			- Note that specs[0][0] has the specs of the 'start_cell' subplot.

			- Each item in 'specs' is a dictionary.
				The available keys are:

				* is_3d (boolean, default=False): flag for 3d scenes
				* colspan (int, default=1): number of subplot columns
					for this subplot to span.
				* rowspan (int, default=1): number of subplot rows
					for this subplot to span.
				* l (float, default=0.0): padding left of cell
				* r (float, default=0.0): padding right of cell
				* t (float, default=0.0): padding right of cell
				* b (float, default=0.0): padding bottom of cell

			- Use 'horizontal_spacing' and 'vertical_spacing' to adjust
			  the spacing in between the subplots.

		insets : list of dicts
			Inset specifications.

			- Each item in 'insets' is a dictionary.
				The available keys are:

				* cell (tuple, default=(1,1)): (row, col) index of the
					subplot cell to overlay inset axes onto.
				* is_3d (boolean, default=False): flag for 3d scenes
				* l (float, default=0.0): padding left of inset
					  in fraction of cell width
				* w (float or 'to_end', default='to_end') inset width
					  in fraction of cell width ('to_end': to cell right edge)
				* b (float, default=0.0): padding bottom of inset
					  in fraction of cell height
				* h (float or 'to_end', default='to_end') inset height
					  in fraction of cell height ('to_end': to cell top edge)
	"""
	if not isinstance(figures,list):
		figures=[figures]

	if shape:
		rows,cols=shape
		if len(figures)>rows*cols:
			raise Exception("Invalid shape for the number of figures given")
	else:
		if len(figures)==1:
			cols=1
			rows=1
		else:
			cols=2
			rows=len(figures)/2+len(figures)%2
	sp=get_subplots(rows=rows,cols=cols,
				  shared_xaxes=shared_xaxes, shared_yaxes=shared_yaxes,
				  start_cell=start_cell, theme=theme,base_layout=base_layout,
				  **kwargs)
	list_ref=(col for row in sp._grid_ref for col in row)
	for i in range(len(figures)):
		while True:
			lr=list_ref.next()
			if lr is not None:
				break
		for _ in figures[i]['data']:
			for axe in lr:
				_.update({'{0}axis'.format(axe[0]):axe})
			sp['data'].append(_)
	# Remove extra plots
	for k in sp['layout'].keys():
		try:
			if int(k[-1])>len(figures):
				del sp['layout'][k]
		except:
			pass
	return sp


def get_subplots(rows=1,cols=1,
				  shared_xaxes=False, shared_yaxes=False,
				  start_cell='top-left', theme='pearl',base_layout=None,
				  **kwargs):

	"""
	Generates a subplot view for a set of figures

	Parameters:
	-----------
		rows : int 
			Number of rows
		cols : int
			Number of cols
		shared_xaxes : bool
			Assign shared x axes.
			If True, subplots in the same grid column have one common
			shared x-axis at the bottom of the gird.
		shared_yaxes : bool
			Assign shared y axes.
			If True, subplots in the same grid row have one common
			shared y-axis on the left-hand side of the gird.
		start_cell : string
				'bottom-left'
				'top-left'
			Choose the starting cell in the subplot grid used to set the
			domains of the subplots.
		theme : string
			Layout Theme
				solar
				pearl
				white		
			see cufflinks.getThemes() for all 
			available themes
		horizontal_spacing : float
				[0,1]
			Space between subplot columns.
		vertical_spacing : float
			Space between subplot rows.
		specs : list of dicts
			Subplot specifications.
				ex1: specs=[[{}, {}], [{'colspan': 2}, None]]
				ex2: specs=[[{'rowspan': 2}, {}], [None, {}]]

			- Indices of the outer list correspond to subplot grid rows
			  starting from the bottom. The number of rows in 'specs'
			  must be equal to 'rows'.

			- Indices of the inner lists correspond to subplot grid columns
			  starting from the left. The number of columns in 'specs'
			  must be equal to 'cols'.

			- Each item in the 'specs' list corresponds to one subplot
			  in a subplot grid. (N.B. The subplot grid has exactly 'rows'
			  times 'cols' cells.)

			- Use None for blank a subplot cell (or to move pass a col/row span).

			- Note that specs[0][0] has the specs of the 'start_cell' subplot.

			- Each item in 'specs' is a dictionary.
				The available keys are:

				* is_3d (boolean, default=False): flag for 3d scenes
				* colspan (int, default=1): number of subplot columns
					for this subplot to span.
				* rowspan (int, default=1): number of subplot rows
					for this subplot to span.
				* l (float, default=0.0): padding left of cell
				* r (float, default=0.0): padding right of cell
				* t (float, default=0.0): padding right of cell
				* b (float, default=0.0): padding bottom of cell

			- Use 'horizontal_spacing' and 'vertical_spacing' to adjust
			  the spacing in between the subplots.

		insets : list of dicts
			Inset specifications.

			- Each item in 'insets' is a dictionary.
				The available keys are:

				* cell (tuple, default=(1,1)): (row, col) index of the
					subplot cell to overlay inset axes onto.
				* is_3d (boolean, default=False): flag for 3d scenes
				* l (float, default=0.0): padding left of inset
					  in fraction of cell width
				* w (float or 'to_end', default='to_end') inset width
					  in fraction of cell width ('to_end': to cell right edge)
				* b (float, default=0.0): padding bottom of inset
					  in fraction of cell height
				* h (float or 'to_end', default='to_end') inset height
					  in fraction of cell height ('to_end': to cell top edge)
	"""
	layout= base_layout if base_layout else getLayout(theme)
	sp=py.plotly.tools.make_subplots(rows=rows,cols=cols,shared_xaxes=shared_xaxes,
										   shared_yaxes=shared_yaxes,print_grid=False,
											start_cell=start_cell,**kwargs)
	for k,v in layout.items():
		if not isinstance(v,XAxis) and not isinstance(v,YAxis):
			sp['layout'].update({k:v})
			
	def update_items(sp_item,layout,axis):
		for k,v in layout[axis].items():
			sp_item.update({k:v})

	for k,v in sp['layout'].items():
		if isinstance(v,XAxis):
			update_items(v,layout,'xaxis')
		elif isinstance(v,YAxis):
			update_items(v,layout,'xaxis')
			
	return sp



def scatter_matrix(df,theme=None,bins=10,color='grey',size=2):
	"""
	Displays a matrix with scatter plot for each pair of 
	Series in the DataFrame.
	The diagonal shows a histogram for each of the Series

	Parameters:
	-----------
		df : DataFrame
			Pandas DataFrame
		theme : string
			Theme to be used (if not the default)
		bins : int
			Number of bins to use for histogram
		color : string
			Color to be used for each scatter plot
		size : int
			Size for each marker on the scatter plot
	"""
	if not theme:
		theme = auth.get_config_file()['theme']
	
	figs=[]
	for i in df.columns:
		for j in df.columns:
			if i==j:
				fig=df.iplot(kind='histogram',keys=[i],asFigure=True,bins=bins)
				figs.append(fig)
			else:
				figs.append(df.iplot(kind='scatter',mode='markers',x=j,y=i,asFigure=True,size=size,colors=[color]))
	layout=getLayout(theme)
	layout['xaxis'].update(showgrid=False)
	layout['yaxis'].update(showgrid=False)
	sm=subplots(figs,shape=(len(df.columns),len(df.columns)),shared_xaxes=False,shared_yaxes=False,
					  horizontal_spacing=.05,vertical_spacing=.07,base_layout=layout)
	sm['layout'].update(bargap=.02,showlegend=False)
	return sm
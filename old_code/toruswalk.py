###
### Python script for creating a pretty picture
### of a random walk in higher dimensions
### using plotly

import plotly
#import plotly.plotly as py
import plotly.figure_factory as FF
import plotly.graph_objs as go
from plotly.graph_objs import *

import numpy as np
from scipy.spatial import Delaunay
#np.set_printoptions(threshold=np.inf)

import random

### Global parameters
am = 1 ## inner radius
rm = 3 ## outer radius
numdiv=50 ## number of divisions in triangulation
num_iter=30 ## number of jumps in the walk

#%%

## Draw torus
u = np.linspace(0, 2*np.pi, numdiv)
v = np.linspace(0, 2*np.pi, numdiv)
U,V = np.meshgrid(u,v)
u = U.flatten()
v = V.flatten()

x = (rm + am*(np.cos(v)))*np.cos(u)
y = (rm + am*(np.cos(v)))*np.sin(u)
z = np.sin(v)

X = (rm + am*(np.cos(V)))*np.cos(U)
Y = (rm + am*(np.cos(V)))*np.sin(U)
Z = np.sin(V)

#print x.shape

points2D = np.vstack([u,v]).T
tri = Delaunay(points2D)
simplices = tri.simplices

plot_data=list()

def dist_origin(x, y, z):
    #return np.sqrt((1.0 * x)**2 + (1.0 * y)**2 + (1.0 * z)**2)
    return y


#data=go.Data([go.Mesh3d(x=x,y=y,z=z,opacity=0.01,colorscale = [['0', 'rgb(255, 0, 255)'], ['0.5', 'rgb(0, 255, 0)'], ['1', 'rgb(0, 0, 255)']])])
torus = FF.create_trisurf(x=x, y=y, z=z, simplices=simplices, title="Torus", aspectratio=dict(x=1, y=1, z=0.3), width=1250, show_colorbar=False)

plot_data.append(torus.data[0])
plot_data.append(torus.data[1])
#%%
### Choose initial column randomly

#colID = random.randint(0,numdiv)
colID=45
#x = (rm+am*np.cos(v))*np.cos(u[colID])
#print type(x)

### Construct it 

trace0 = go.Scatter3d(
        x = (rm+am*np.cos(v))*np.cos(u[colID]),
        y = (rm+am*np.cos(v))*np.sin(u[colID]),
        z= am*np.sin(v),
        marker=dict(
            size=1,
            color='red',
        ),
        line=dict(
             color='red',
             width=4,
        ),
        name='original cycle-0',
)
plot_data.append(trace0)


frames=list()
#torus['data'].extend(go.Data([trace0]))
#%%     
### Randomize the movement of the cycle
### Iterate 10 times
for iter in range(num_iter):
    #print "Run number"
    #print iter
    deviation = np.zeros(numdiv) 
    devID = random.randint(0,numdiv-1) # radomly choose a meridian vertex to change
    nearbyDevID = random.randint(0,1) # randomly choose one side of the vertex to accompany the jump
                                      # this probably isn't necessary for the simplicial complex version of the
                                      # torus that is currently implemented. This was used for the square decomposition
                                      # of old.
    orientID = random.randint(0,1) # randomly choose which side to jump on, i.e., in CW or CCW direction.
    if nearbyDevID == 1:
        if orientID == 1:
            deviation[(devID % numdiv)] = -1
        else:
            deviation[(devID % numdiv)]=1
    else:
        if orientID == 1:
            deviation[(devID % numdiv)] = -1
        else:
            deviation[(devID % numdiv)]=1
    
    #print deviation
    #deviation = [0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    colID = colID + deviation ### Add deviation to cycle
    if (iter +1) % 2 == 0: ### Add drift
        drift = np.ones(numdiv) 
        colID = colID + drift

    xd = np.insert(np.repeat(np.arange(start=1,stop=numdiv),2),0,0)
    yd = np.repeat(colID,2).astype(int)
    yd = yd[:-1]

    colX = [] #np.zeros(xd.size)
    colX.append(xd[0]) #colX[0] = xd[0]
    colY = [] #np.zeros(yd.size)
    colY.append(yd[0]) #[0] = yd[0]
    #%%
    k=2
    for t in range(1,yd.size):
        if np.int(np.sign(yd[t]-yd[t-1])) > 0:
            inc = 1
        if np.int(np.sign(yd[t]-yd[t-1])) < 0:
            inc = -1
        if np.int(np.sign(yd[t]-yd[t-1])) == 0:
            inc = 0
        #%%
        if inc ==0: # the yd entries are the same, update them and re-iterate.
            colX.append(xd[t])
            colY.append(yd[t])
            continue
        else:
            ids = list(range(np.int(yd[t-1]),np.int(yd[t]),inc))
            if ids == []:
                n=0
                ids = yd[t]
            else:
                ids.pop(0)
                n=len(ids)
        for l in range(k,k+n):
            colX.append(xd[t-1])
            colY.append(ids[l-k])
        k=k+n
    if colY[-1] != colY[0]: # if you don't end where you start
        if np.int(np.sign(colY[-1]-colY[0])) > 0:
            ids = range(np.int(colY[-1]),np.int(colY[0])-1,-1)
        if np.int(np.sign(colY[-1]-colY[0])) < 0:
            ids = range(np.int(colY[-1]),np.int(colY[0])+1,1)
        for l in ids:
            colY.append(l)
            colX.append(colX[-1])
    
    
    npColX = np.array(colX)
    npColY = np.array(colY)
    npt = npColX.size


    xcj = np.zeros(npt)
    ycj = np.zeros(npt)
    zcj = np.zeros(npt)           
    for k in range(npt):
        xcj[k] = X[(np.int(npColX[k]) % numdiv),(np.int(npColY[k]) % numdiv)]
        ycj[k] = Y[(np.int(npColX[k]) % numdiv),(np.int(npColY[k]) % numdiv)]
        zcj[k] = Z[(np.int(npColX[k]) % numdiv),(np.int(npColY[k]) % numdiv)]
    trace1= go.Scatter3d(
        x = xcj, 
        y = ycj, 
        z= zcj, 
        marker=dict(
            size=1,
            color='blue',
        ),
        line=dict(
             color='blue',
             width=4,
        ),
        name="Pert. number {}".format(iter+2)
    )
    plot_data.append(trace1)
    sliders_dict={'steps':[]}
    frame = {'data': []}
    data_dict = {
            'method':'restyle',
            'args':['visible', [True],
              {'frame': {'duration':300, 'redraw':False},
               'mode':'immediate',
               'transition':{'duration':300}}],
    }
    frame['data'].append(data_dict)
    frames.append(frame)

steps = list()
#layout=list()
frames = list()

for i in range(num_iter+4): #two torus traces, plus the initial cycle, plus python indexing
        step = dict(
        method='restyle',
        args=[
              'visible', [False] * (num_iter+4),
              {'frame': {'duration':300, 'redraw':False},
               'mode':'immediate',
               'transition':{'duration':300}}],
        label='yy {}'.format(i), ##marker on slider and above slider
        #value=i,
        )
        step['args'][1][i] = True #display current frame
        step['args'][1][0] = True #display smooth torus
        step['args'][1][1] = True #display triangulation
        step['args'][1][2] = True #display initial cycle
        #step['args'][1][i * 2 + 1] = True
        steps.append(step)
        frame = {'data': [], 'name':'{}'.format(i-1)}
        frame['data'].append(step)
        frames.append(frame)
        

       
#for i in range(1,num_iter+4): 
#    sliders_dict={'steps':[]}
#    frame = {'data': []}
#    for step in steps:
#        data_dict = {
#            'method':'restyle',
#            'args':['visible', [False] * (num_iter+3),
#              {'frame': {'duration':300, 'redraw':False},
#               'mode':'immediate',
#               'transition':{'duration':300}}]#,
#            #'name': '{}'.format(step['value'])
#        }
#        frame['data'].append(data_dict)
#    frames.append(frame)
#    slider_step = {'args': [
#        [],
#        {'frame': {'duration': 300, 'redraw': False},
#         'mode': 'immediate',
#       'transition': {'duration': 300}}
#     ],
#     'label': i,
#     'method': 'animate'}
#    sliders_dict['steps'].append(slider_step)
    
    
#        step = dict(
#        method='animate',
#        args=['visible', [False] * (num_iter+3),
#              {'frame': {'duration':300, 'redraw':False},
#               'mode':'immediate',
#               'transition':{'duration':300}}],
#        label='{}'.format(i-2),
#        value=i,
#        )
#        step['args'][1][i] = True
#        step['args'][1][0] = True
#        step['args'][1][1] = True
#        step['args'][1][2] = True
#        #step['args'][1][i * 2 + 1] = True
#        #steps.append(step)
#        frame = {'data': [], 'name':str(i)}
#        frame['data'].append(step)
#        frames.append(frame)

sliders = [dict(
    steps=steps,
    transition={'duration':300},
    active=0,
    currentvalue={
        'font': {'size': 20},
        'prefix': 'text-before-value-on-display',
        'visible': True,
        'xanchor': 'right'
    },
)]


layout = dict(
    width=1000,
    height=800,
    autosize=False,
    sliders=sliders,
    )

fig=dict(data=plot_data,layout=layout,frames=frames)

for i in range(3,num_iter+3):
    fig['data'][i].update(opacity=0.25)
fig['data'][0].update(opacity=0.5)
fig['data'][1].update(opacity=0.25)


fig['layout']['updatemenus'] = [
    {
        'buttons': [
            {
                'args': [None, {'frame': {'duration': 300, 'redraw': False},
                         'fromcurrent': True, 'transition': {'duration': 300, 'easing': 'quadratic-in-out'}}],
                'label': 'Play',
                'method': 'animate'
            },
            {
                'args': [[None], {'frame': {'duration': 0, 'redraw': False}, 'mode': 'immediate',
                'transition': {'duration': 0}}],
                'label': 'Pause',
                'method': 'animate'
            }
        ],
        'direction': 'left',
        'pad': {'r': 50, 't': 100},
        'showactive': False,
        'type': 'buttons',
        'x': 0.1,
        'xanchor': 'right',
        'y': 0,
        'yanchor': 'top'
    }
]


#fig['layout']['sliders'] = {
#    'active': 0,
#    #'yanchor': 'top',
#    #'xanchor': 'left',
#    'currentvalue': {
#        'font': {'size': 20},
#        'prefix': 'text-before-value-on-display',
#        'visible': True,
#        'xanchor': 'right'
#    },
#    'transition': {'duration': 300, 'easing': 'cubic-in-out'},
#    #'pad': {'b': 10, 't': 50},
#    #'len': 0.9,
#    #'x': 0.1,
#    #'y': 0,
#    'steps': steps
#}

fig['layout']['slider'] = {
    'args': [
        'slider.value', {
            'duration': 300,
            'ease': 'cubic-in-out'
        }
    ],
    'initialValue': '2',
    'plotlycommand': 'animate',
    'values': list(range(2,num_iter+4)),
    'visible': True
}


plotly.offline.plot(fig,validate=False,filename='Torus_walk_slider.html')
#plotly.offline.plot(data,filename='./scatter_test.html')

#plot = plotly.offline.plot(new_trace, filename='./Torus_with_circle.html',fileopt='append')
#!/usr/bin/env python

import math
import pylab # matplotlib
 
#
# create the x list data
#
# arange() is just like range() but allows float numbers
#
x_list = pylab.arange(0.0, 5.0, 0.01)
#
 
#
# calculate the y list data
#
y_list = []
#
for x in x_list:
  y = math.cos(2*math.pi*x) * math.exp(-x)
  y_list.append(y)
#
 
#
pylab.xlabel("x")
#
pylab.ylabel("cos(2pi * x) * exp(-x)")
#
 
#
# draw the plot with a blue line 'b' (is default)
#
# using x,y data from the x_list and y_list
#
# (these lists can be brought in from other programs)
#
#
#
# other drawing styles -->
#
# 'r' red line, 'g' green line, 'y' yellow line
#
# 'ro' red dots as markers, 'r.' smaller red dots, 'r+' red pluses
#
# 'r--' red dashed line, 'g^' green triangles, 'bs' blue squares
#
# 'rp' red pentagons, 'r1', 'r2', 'r3', 'r4' well, check out the markers
#
#
#
pylab.plot(x_list, y_list, 'b')
#
 
#
# save the plot as a PNG image file (optional)
#
pylab.savefig('Fig1.png')

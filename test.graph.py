#!/usr/bin/env python

from pylab import *

def main():  
    my_dict = {'A': 70, 'B': 290, 'C': 130}
    bar_graph(my_dict, graph_title='ABC')


def bar_graph(name_value_dict, graph_title='', output_name='bargraph.png'):
    figure(figsize=(4, 2)) # image dimensions  
    title(graph_title, size='x-small')
   
    # add bars
    for i, key in zip(range(len(name_value_dict)), name_value_dict.keys()):
        bar(i + 0.25 , name_value_dict[key], color='red')
   
    # axis setup
    xticks(arange(0.65, len(name_value_dict)),
        [('%s: %d' % (name, value)) for name, value in
        zip(name_value_dict.keys(), name_value_dict.values())],
        size='xx-small')
    max_value = max(name_value_dict.values())
    tick_range = arange(0, max_value, (max_value / 7))
    yticks(tick_range, size='xx-small')
    formatter = FixedFormatter([str(x) for x in tick_range])
    gca().yaxis.set_major_formatter(formatter)
    gca().yaxis.grid(which='major')
   
    savefig(output_name)


if __name__ == "__main__":
    main()

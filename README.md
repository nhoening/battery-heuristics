battery-heuristics
==================

Code to run computational simulations for a paper submitted to CIASG 2013.
(paper is under submission).

Contact: nicolas@cwi.nl


Requirements
-------------

Running algorithms:
* [Python 2.7+](http://python.org/)
* [GLPK (GNU Linear Programming Kit)](http://www.gnu.org/software/glpk/)
* [pymprog](http://pymprog.sourceforge.net/)

Conduct experiments and plot graphs:
* [nicessa](http://homepages.cwi.nl/~nicolas/nicessa/)
* [Gnuplot](http://www.gnuplot.info/)

Running simulations
--------------------

Running all scenarios:

``nicessa --run``

Running a specific scenario:

``nicessa --sim nonadaptive_optimistic --run``

Generating plots is done by replacing the ``--run`` parameter with ``--plots``.

By turning on the debug option in ``nicessa.conf``, more output can be generated
to study what is going on.
(then, it might be useful to also set the ``runs`` option down from 20 to 1 and 
in ``main.py`` edit the list of battery types and ``w`` values that are run).

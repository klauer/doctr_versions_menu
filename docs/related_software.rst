================
Related software
================

* Doctr_: A tool for automatically deploying docs from `Travis CI`_ to `GitHub Pages`_. The ``doctr-versions-menu`` package works in conjuntion with Doctr to inject a versions menu into the documentation.
* Sphinx_: Documentation generator. While Doctr_ does no require the use of Sphinx, the ``doctr-versions-menu`` package works as a Sphinx extension.
* `Read the Docs`_ (RTD): Widely used documentation hoster. The motivation behind the ``doctr-version-menu`` is to provide a versions menu nearly idential to the one injected by RTD. As the versions menu injected by ``doctr-versions-menu`` was reverse-engineered directly from the RTD menu, the package includes CSS develped by `Read the Docs`_.
* `Read the Docs Sphinx Theme`_: The recommended theme for Sphinx documentation (even when not hosted on ``readthedocs.org``). While ``doctr-versions-menu`` should work to inject a versions menu into any theme, the original RTD theme best integrates the menu.

.. _Doctr: https://drdoctr.github.io
.. _Travis CI: https://travis-ci.org
.. _Github Pages: https://pages.github.com
.. _Sphinx: https://www.sphinx-doc.org
.. _Read the Docs: https://github.com/readthedocs/readthedocs.org
.. _Read the Docs Sphinx Theme: https://sphinx-rtd-theme.readthedocs.io/
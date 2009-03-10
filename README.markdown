AGRO
----

Aggregates personal online activity with plug-in based architecture.

Agro is a small, streamlined, simple feed/activity aggregator. The (released) feature set is simple, but with the ability to write your own plugins, the possibilities are endless. If you do write a plug-in, let me know and I'll include it in a source repo here.

BUILT-IN
========

Twitter, flickr, last.fm and delicious. 

INSTALL
=======

Check the [http://code.google.com/p/agroapp/wiki/Settings settings] wiki page on how to 'install' agro.
Default sources require [http://code.google.com/p/django-tagging/ django-tagging].

************

CHANGELOG
---------
09/08/2008
==========

Can now use signed calls to get non-public data, original_secret, etc from non-CC licensed photos!
Set up an API_Key, and [http://camronflanders.com/agro/flickr_token_gen/ visit this page.]

08/19/2008
==========

Command line arguments!

The ability to update only certain sources was added a while back, but now we can force update.  [http://code.google.com/p/agroapp/wiki/retrievePy see the wiki page]

08/07/2008
==========

Can now aggregate for multiple accounts on every plugin!_*===

08/05/2008
==========

Template tags added.
2 template tags have been added.
[http://code.google.com/p/agroapp/wiki/TemplateTags see wiki page]

*************

_agro is developed on django trunk and is inspired by jellyroll (from Jacob Kaplan-Moss)._

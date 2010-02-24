clean:
	find -name "*~"| xargs rm -f
	find -name "*pyc"| xargs rm -f
	rm -f webpanel/sessions/* python-build-stamp*
	rm -rf ThinFilter.egg-info build
	fakeroot debian/rules clean
	dh_clean

superclean: clean
	rm -rf thinfilter.db thinfilter.log


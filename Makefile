clean:
	find -name "*~"| xargs rm -f
	find -name "*pyc"| xargs rm -f
	rm -f webpanel/sessions/* python-build-stamp*
	rm -rf ThinFilter.egg-info build
	find squidGuard/db/ -name "*.db"| xargs sudo rm -f
	debian/rules clean


superclean: clean
	rm -rf thinfilter.db thinfilter.log


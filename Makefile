

clean:
	find -name "*~"| xargs rm -f
	find -name "*pyc"| xargs rm -f
	rm -f webpanel/sessions/*

superclean: clean
	rm -rf thinfilter.db thinfilter.log

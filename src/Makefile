.PHONY: clean_output ktree prob_tree markov_tester
all: ktree prob_tree markov_tester sp500

default_deps: graphviz.py tree.py

ktree: output/ktrees.html
prob_tree: output/prune_tree.svg
prob_tree_png: output/prune_tree.png
markov_tester: output/markov_tester.svg
sp500: output/sp500.svg

output/%.png: output/%.dot
	dot $< -o $@ -Tpng

output/%.svg: output/%.gv
	dot $< | gvpack -g | dot -o $@ -Tsvg

output/%.svg: output/%.dot
	dot $< -o $@ -Tsvg

output/ktrees.html: kTree.py $(default_deps)
	python3 kTree.py html > $@

output/prune_tree.dot: prob_tree.py $(default_deps)
	python3 prob_tree.py > $@

output/markov_tester.gv: markov_tester.py $(default_deps)
	python3 markov_tester.py > $@

output/sp500.dot: sp500.py $(default_deps)
	python3 sp500.py > $@

clean_output:
	rm output/*.dot output/*.svg output/*.html

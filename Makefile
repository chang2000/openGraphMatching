uploadofficial:
	make clean
	python setup.py sdist bdist_wheel
	twine upload dist/*

uploadtest:
	make clean
	python setup.py sdist bdist_wheel
	twine upload --repository testpypi dist/*

clean:
	rm -rf *.egg-info, dist

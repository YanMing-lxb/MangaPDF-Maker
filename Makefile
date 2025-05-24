all:
pack:
	@python ./tools/pack.py pack

setup:
	@python ./tools/pack.py setup

upload:
	@python ./tools/make.py upload